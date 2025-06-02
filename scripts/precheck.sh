REQUIRED_BINS=("brew")

for bin in "${REQUIRED_BINS[@]}"; do
	if ! command -v $bin > /dev/null 2>&1; then
		echo "Error: Please install '$bin', consulting README.md"
		exit 1
	fi
done

if ! command -v pyenv > /dev/null 2>&1; then
	echo "Installing pyenv via Homebrew"
	brew install pyenv
	echo "\033[92mPyenv Installed\033[0m"
fi

if ! command -v pipenv > /dev/null 2>&1; then
	echo "Installing pipenv via Homebrew"
	brew install pipenv
	echo "\033[92mPipenv Installed\033[0m"
fi

if ! grep -q 'pyenv init' ~/.zshrc; then
	echo "Adding pyenv init to .zshrc"
	echo 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$$(pyenv init -)"\nfi' >> ~/.zshrc
	echo '\033[92mYour ~/.zshrc has been altered. Please run "source ~/.zshrc" then rerun your make command\033[0m'
	exit 1
fi

echo "\033[92mPrechecks successful.\033[0m"