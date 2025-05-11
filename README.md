<!-- Title: Clearly state the project name and give a brief tagline -->
# PrintSync: A Printing Kiosk and Mobile Interface Solution

A full-stack web application for a printing kiosk system with intuitive kiosk and mobile interfaces, designed to streamline document printing with features like PDF ink cost estimation, UPI payments, and dynamic print options.

<!-- Badges: Optional, to show build status, license, or tech stack. Uncomment if you use CI/CD or want to highlight tools. -->
<!-- [![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://www.python.org/) -->
<!-- [![Flask](https://img.shields.io/badge/Flask-2.0+-black)](https://flask.palletsprojects.com/) -->

---

<!-- Overview: Summarize the project, its purpose, and key features. This is an elaboration of your submission statement. -->
## Overview

**PrintSync** is a submission for a printing kiosk system, featuring a dual-interface solution for both kiosk operators and mobile users. The project provides a seamless, user-friendly experience for printing documents, with a web-based kiosk dashboard and a mobile-optimized interface for customers. Built with Flask and Python, it integrates PDF processing, cost estimation, and UPI payment functionality, making it ideal for small-scale printing businesses or campus kiosks.

### Key Features
- **Kiosk Interface**: Real-time file management, QR code connectivity, and print job processing for operators.
- **Mobile Interface**: Upload PDFs, select print options (paper size, finish, B/W or color), and pay via UPI QR codes.
- **Ink Cost Estimation**: Calculates costs based on character count for B/W prints; color prints are charged at a hidden 5x multiplier.
- **Dynamic Print Options**: Choose A4/A3, matte/glossy, and B/W or color printing.
- **Secure File Handling**: Temporary storage of uploaded PDFs, auto-deleted after printing.
- **Local Network Deployment**: Connects mobile devices to the kiosk via QR code scanning over a local network.

<!-- Purpose: Explain why this section exists. It gives context for evaluators or users to understand the project’s scope and intent. -->

---

<!-- Directory Structure: Address the logo issue by clearly defining where files should go, especially static/Logoo.jpg. -->
## Directory Structure

To ensure the application runs correctly (e.g., logo display on the host page), follow this directory hierarchy:
PrintSync/
├── test.py              # Main Flask application script
├── static/              # Static assets (e.g., logo)
│   └── Logoo.jpg        # Logo image for kiosk interface (ensure exact filename)
├── uploads/             # Auto-created for uploaded PDFs
└── README.md            # This file


**Note**: The logo (`Logoo.jpg`) must be placed in the `static/` folder. If missing or misnamed (e.g., `logo.jpg`), the host page (`/host`) will show a broken image. Create the `static/` folder manually if it doesn’t exist.

<!-- Purpose: Clarifies file placement to prevent issues like the logo not showing, as per your earlier question. -->

---

<!-- Installation: Provide step-by-step setup instructions for running the project. -->
## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Steps
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/BPstech/PrintSync.git
   cd PrintSync


Acknowledgments
Built with Flask and PyPDF2.

Background images sourced from Pexels.

Inspired by modern printing kiosk workflows.

