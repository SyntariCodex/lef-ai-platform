#!/bin/bash

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get the absolute path of the installation directory
INSTALL_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${BLUE}Installing LEF Development Environment...${NC}"

# Create LEF directory in home
mkdir -p ~/.lef

# Create a config file
cat > ~/.lef/config << EOF
# LEF Configuration
LEF_PROJECT_ROOT="$INSTALL_DIR"
EOF

# Create the launcher script
cat > /usr/local/bin/lef << EOF
#!/bin/bash
source ~/.lef/config
cd "\$LEF_PROJECT_ROOT" && ./start_lef.sh "\$@"
EOF

# Make the launcher executable
chmod +x /usr/local/bin/lef

echo -e "${GREEN}✓ LEF installed successfully!${NC}"
echo -e "${BLUE}You can now run LEF from anywhere using the 'lef' command${NC}" 