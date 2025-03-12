# KI Admin Panel

Welcome to the KI Admin Panel project! First of all this is a Tattle ;-) \
When you use a docker an mount a Windows directory watchdog doesn't send any events. \
So this app runs locally on a Windows PC an tattles all these events towards an API. \
And if the app already exists, you can also do a few admin things. \
Have fun

![Screenshot](/assets/Screenshot.png)

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Introduction

The KI Admin Panel is a fat client application designed to manage and monitor the ki-tools API. It provides an interface for administrators an tattles modification events to that API.

## Features

- send file events
- Dashboard for monitoring AI model performance

## Installation

There is no installation, just start the .exe file

## Build .exe with pyinstaller

use ```console=True``` in main.spec to see the console window while running
Start packaging: ```poetry run pyinstaller main.spec```

## Usage

TODO: later

### logfile

You'll find the logfile at `C:\Users\<username>\.tattle`

## Contributing

We welcome contributions to the KI Admin Panel project! If you would like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes and push them to your fork.
4. Submit a pull request with a detailed description of your changes.

## Info

python = ">=3.12,<3.14" is because of pyinstallerpyinstaller --onefile --noconsole your_app.py
Icon source: [Google Icons](https://fonts.google.com/icons)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
Check the license for Google Icons. I don't know that.
