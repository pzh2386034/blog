#! /bin/bash

# _deploy.sh

echo "Building jekyll..."
bundle install
bundle exec jekyll build
echo "Building complete!"

echo "Deploying to serve..."
bundle exec jekyll serve --config _config.yml,_config_dev.yml
# rsync -vrzc  --delete --rsh='ssh -p<your_ssh_port>' _site/ user@example.com:<your_public_folder>
echo "Deploying complete!"
