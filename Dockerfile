#  Copyright 2016 IBM
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

FROM node
MAINTAINER Philippe Mulet "philippe_mulet@fr.ibm.com"

# Install the application
ADD package.json /app/package.json
RUN cd /app && npm install  
ADD app.js /app/app.js
ENV WEB_PORT 80
EXPOSE  80

# Set password length and expiry for compliance with vulnerability advisor
RUN sed -i 's/ˆPASS_MAX_DAYS.*/PASS_MAX_DAYS   90/' /etc/login.defs
RUN sed -i 's/sha512/sha512 minlen=8/' /etc/pam.d/common-password

# Remove SSH for compliance with vulnerability advisor
# RUN apt-get purge -y openssh-server
# RUN apt-get remove -y openssh-sftp-server
# RUN apt-get -y autoremove

# Define command to run the application when the container starts
CMD ["node", "/app/app.js"] 

