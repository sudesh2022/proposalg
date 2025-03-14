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

# Vulnerability Advisor : uninstall openssh-server
# RUN apt-get --purge remove openssh-server

# Vulnerability Advisor : Fix PASS.MAX.DAYS and PASS.MIN.LEN
RUN mv -f /etc/login.defs /etc/login.defs.orig
RUN sed 's/^PASS_MAX_DAYS.*/PASS_MAX_DAYS 90/' /etc/login.defs.orig > /etc/login.defs
RUN grep -q '^PASS_MIN_LEN' /etc/login.defs && sed -i 's/^PASS_MIN_LEN.*/PASS_MIN_LEN 8/' /etc/login.defs || echo 'PASS_MIN_LEN 9\n' >> /etc/login.defs
RUN grep -q '^password.*required' /etc/pam.d/common-password && sed -i 's/^password.*required.*/password    required            pam_permit.so minlen=9/' /etc/pam.d/common-password || echo 'password    required            pam_permit.so minlen=9' >> /etc/pam.d/common-password

# Define command to run the application when the container starts
CMD ["node", "/app/app.js"] 

