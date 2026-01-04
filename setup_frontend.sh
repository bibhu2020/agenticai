
#!/bin/bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

if ! command -v node &> /dev/null
then
    echo "Node not found"
    exit 1
fi

echo "Node version: $(node -v)"
echo "NPM version: $(npm -v)"

# Clean previous failed attempts
rm -rf src/medibo/frontend

# Create App
npx -y create-vite@latest src/medibo/frontend --template react

# Install deps
cd src/medibo/frontend
npm install
