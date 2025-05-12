# 🎯 Object & Activity Recognition App

[![Streamlit App](https://img.shields.io/badge/Launch%20App-Click%20Here-brightgreen?style=for-the-badge)](https://ex-oar.streamlit.app/)

This interactive app helps users extract **object types**, **activities**, and **objects** from unstructured or semi-structured textual data (e.g., window titles), with support from **GPT-4.1** and domain knowledge.

Designed for **desk-oriented workers**, the tool supports the generation of **object-centric event logs** for process mining or other analysis purposes.

## 🚀 Try the App

👉 [Launch the app](https://ex-oar.streamlit.app/)

## 🧠 Key Features

- **Step-by-step guidance** through 5 interactive stages:
  1. Identify object types  
  2. Identify activities  
  3. Detect concrete object instances  
  4. Enrich window titles with objects & activities  
  5. Export structured results as JSON

- Use **predefined options** or generate domain-specific data using **OpenAI's GPT-4.1**

- Lightweight, **privacy-preserving** local use: user data is never stored or shared

- Designed for integration with **object-centric event log generation pipelines**

## 📂 How to Use Locally

1. Clone this repo  
2. Run with Streamlit:  
   ```bash
   streamlit run Home.py
3. Enter your OpenAI API key and upload your Tockler CSV data
4. Walk through each step and export your results at the end

Note: You will need a valid OpenAI API key to use GPT-enhanced functionality.

## 📢 Citation / Research Use
This app is part of a research project by Iris Beerepoot, Vinicius Stein Dani, and Xixi Lu.
Participants in the evaluation study can export their results in the final step and send the JSON file to the research team manually.

## 🔐 Data Privacy
✅ Your data is used only within the current session
✅ All processing happens locally, except for GPT completions
✅ No input is stored or shared unless you export it yourself

## 🤝 Contributions
Contributions and feature suggestions are welcome! Please open an issue or submit a pull request.

