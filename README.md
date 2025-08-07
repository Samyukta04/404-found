# Credit Intelligence Engine

## Overview

This project is a real-time AI-powered credit optimization platform built with Streamlit. It integrates live market data and real customer inputs to provide intelligent credit limit recommendations and detailed portfolio analytics. It also features secure user authentication using Google OAuth 2.0.

## Features

- Real-time credit portfolio management with AI-driven decisioning.
- Live integration of financial market data (S&P 500, VIX, Treasury rates).
- Interactive customer data input and personalized AI credit recommendations.
- Portfolio metrics, utilization and opportunity visualizations using Plotly.
- AI-powered strategic analysis of customer credit profiles.
- Compliance and bias detection considerations embedded in design.

## Setup Instructions

1. **Clone the repository:**

```bash
git clone 
cd 
```

2. **Create and activate a Python virtual environment:**

On Windows:
```bash
python -m venv venv
.\venv\Scripts\activate
```

On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install Python dependencies:**

```bash
pip install -r requirements.txt
```

4. **Create a `.env` file in the root directory** with the following environment variables:

```
GROQ_API_KEY=your_groq_api_key_here

```
- Replace the placeholders with your actual keys.

## Running the Application

Execute the following command to start the Streamlit app:

```bash
streamlit run app.py
```

- The app will open in your default web browser.
- You can input customer data, view AI recommendations, analyze portfolio metrics, and interact with the credit intelligence engine.


