#!/bin/bash
echo -e "Build environment variables:"
echo "REGISTRY_URL=${REGISTRY_URL}"
echo "REGISTRY_NAMESPACE=${REGISTRY_NAMESPACE}"
echo "IMAGE_NAME=${IMAGE_NAME}"
echo "BUILD_NUMBER=${BUILD_NUMBER}"

# Learn more about the available environment variables at:
# https://console.bluemix.net/docs/services/ContinuousDelivery/pipeline_deploy_var.html#deliverypipeline_environment

# To review or change build options use:
# bx cr build --help

echo -e "Checking for Dockerfile at the repository root"
if [ -f Dockerfile ]; then 
   echo "Dockerfile found"
else
    echo "Dockerfile not found"
    exit 1
fi

echo -e "Building container image"
set -x
bx cr build -t $REGISTRY_URL/$REGISTRY_NAMESPACE/$IMAGE_NAME:$BUILD_NUMBER .
set +x

echo -e "Copying artifacts needed for deployment and testing"

# IMAGE_NAME from build.properties is used by Vulnerability Advisor job to reference the image qualified location in registry
echo "IMAGE_NAME=${REGISTRY_URL}/${REGISTRY_NAMESPACE}/${IMAGE_NAME}:${BUILD_NUMBER}" >> $ARCHIVE_DIR/build.properties

# RELEASE_NAME from build.properties is used in Helm Chart deployment to set the release name
echo "RELEASE_NAME=${IMAGE_NAME}" >> $ARCHIVE_DIR/build.properties

if [ -f ./chart/${CHART_NAME}/values.yaml ]; then
    #Update Helm chart values.yml with image name and tag
    echo "UPDATING CHART VALUES:"
    sed -i "s~^\([[:blank:]]*\)repository:.*$~\1repository: ${REGISTRY_URL}/${IMAGE_NAME}~" ./chart/${CHART_NAME}/values.yaml
    sed -i "s~^\([[:blank:]]*\)tag:.*$~\1tag: ${APPLICATION_VERSION}~" ./chart/${CHART_NAME}/values.yaml
    cat ./chart/${CHART_NAME}/values.yaml
    cp -r ./chart/ $ARCHIVE_DIR/
else 
    echo -e "${red}Helm chart values for Kubernetes deployment (/chart/${CHART_NAME}/values.yaml) not found.${no_color}"
    exit 1
fi     
