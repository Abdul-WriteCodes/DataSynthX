

# ⬡ DataSynthX
<p align="center">
  <img src="assets/Dx1.jpeg" alt="DataSynthX Logo" width="800"/>
</p>


DataSynthX is an AI-powered platform that enable users to generate useful synthetic data by learning the statistical DNA of the data. It makes synthetic data data generation simple by:
- Enabling user upload any dataset
- Learn its structure and statistical DNA
- Generate high-fidelity synthetic data
- Compute trust & validation metrics
- Use AI to explain everything in plain English

>While most tools generate synthetic data, DataSynthX shows and tells you if you can trust and use it

---

## ⚡ Key Features

-	🔬Statistical Profiling Engine

	- Automatic detection:
	- Numeric, categorical, datetime columns
	- Deep statistical extraction:
		  - Mean, variance, skewness, kurtosis
		  - Missing value patterns
		  - Correlation matrix

---

### 🧬 2. Synthetic Data Generation Engine

* **Multivariate Gaussian modeling** (numeric)
* **Frequency-preserving sampling** (categorical)
* **Missing value replication**
* **Noise injection for realism**
* Scales to **hundreds of thousands of rows**

---

### 📊 3. Trust & Fidelity Metrics

* Correlation Preservation Score
* Distribution Similarity:

  * Kolmogorov-Smirnov Test
  * Wasserstein Distance
* Synthetic Consistency Index (SCI)

---

### 🤖 4. AI Insight Explainer (GAME CHANGER)

> This is what makes DataSynthX different.

* Interprets:

  * Statistical distributions
  * Correlation structures
  * Synthetic vs real differences
* Explains:

  * What changed
  * What stayed consistent
  * Whether the data is reliable
* Outputs:

  * Human-readable insights
  * Research-ready explanations

✅ No statistical expertise required
✅ Turns numbers into **understanding**

---

### 💳 5. Credit-Based Access System

* Google Sheets-powered backend
* Secure access keys (`DSX-XXXX-XXXX`)
* 1 generation = 1 credit
* Credits never expire

---

### 📤 6. Export Ready

* CSV download
* Excel download
* Ready for:

  * Research
  * ML pipelines
  * Testing environments

---

## 🧠 How It Works

```text
Upload Data → Profile → Generate → Validate → Explain → Export
```

### Step-by-step:

1. **Upload**

   * CSV / Excel dataset

2. **Profile**

   * Statistical structure extracted

3. **Generate**

   * Synthetic dataset created

4. **Validate**

   * Fidelity metrics computed

5. **Explain (AI Layer)**

   * AI interprets results
   * Highlights reliability + risks

6. **Export**

   * Download synthetic dataset

---

## 🏗️ Architecture

```text
DataSynthX
│
├── Frontend (Streamlit)
│   ├── Landing Page
│   ├── Upload Interface
│   ├── Visualization Dashboard
│
├── Core Engines
│   ├── DataProfiler
│   ├── SyntheticDataGenerator
│   ├── TrustMetrics
│
├── AI Layer
│   ├── OpenAI Integration
│   │   ├── Statistical Insight Explanation
│   │   ├── Synthetic vs Real Comparison
│   │   └── Data Reliability Narratives
│
└── Credit Engine
    ├── Google Sheets (gspread)
    ├── Access Key Validation
    └── Credit Deduction Logic
```

---

## 🧪 Core Components

### `DataProfiler`

Extracts full statistical structure from raw datasets.

### `SyntheticDataGenerator`

Generates synthetic data while preserving:

* Distributions
* Correlations
* Missing patterns

### `TrustMetrics`

Evaluates how “real” your synthetic data is.

### `AIExplainer`

Transforms metrics into:

* Insights
* Interpretations
* Decisions

---

## 🔐 Privacy by Design

* No raw data storage
* Synthetic output is non-identifiable
* Built for:

  * Compliance
  * Secure data sharing
  * Safe experimentation

---

## 💡 Use Cases

* 📊 Machine Learning training datasets
* 🧪 Academic & research simulations
* 🏥 Healthcare data (privacy-safe)
* 💳 Financial modeling
* 🔍 Data analysis without exposure
* 🧠 AI-assisted statistical interpretation

---

## 🛠️ Tech Stack

* **Frontend:** Streamlit
* **Backend:** Python
* **Data Processing:** Pandas, NumPy, SciPy
* **Visualization:** Plotly
* **Auth & Credits:** Google Sheets (gspread)
* **AI Engine:** OpenAI API

---

## ⚙️ Installation

```bash
git clone https://github.com/yourusername/datasynthx.git
cd datasynthx
pip install -r requirements.txt
```

---

## 🔑 Environment Setup

Create `.streamlit/secrets.toml`:

```toml
[gcp_service_account]
type = "service_account"
project_id = "..."
private_key = "..."
client_email = "..."

DSX_SHEET_ID = "your_sheet_id"
OPENAI_API_KEY = "your_openai_key"
```

---

## ▶️ Run Locally

```bash
streamlit run app.py
```

---

## 📈 Roadmap

* [ ] Differential Privacy Integration
* [ ] Time-Series Synthetic Data
* [ ] FastAPI API Access
* [ ] Batch Dataset Processing
* [ ] Team Collaboration Features
* [ ] Dataset Versioning

---

## 🤝 Contributing

Pull requests are welcome.
For major changes, open an issue first.

---

## 📩 Support

* Email: [Abdulwrite77@gmail.com](mailto:Abdulwrite77@gmail.com)
* WhatsApp: +2348096506034

---

## 📄 License

MIT License

---

## ⚡ Final Thought

> Data is not useful unless it is understood.

**DataSynthX doesn’t just generate data.
It makes data make sense.**
# ⬡ DataSynthX

### **Generate Data That Looks Real, Behaves Real — and Explains Itself**

> Privacy-Safe Synthetic Data + AI-Powered Statistical Insight Engine

---

## 🚀 What is DataSynthX?

**DataSynthX** is an AI-powered platform that doesn’t just generate synthetic data —
it **understands it, validates it, and explains it**.

Upload any dataset, and DataSynthX will:

1. Learn its **statistical DNA**
2. Generate **high-fidelity synthetic data**
3. Compute **trust & validation metrics**
4. Use AI to **explain everything in plain English**

---

## 🔥 Core Value Proposition

> Most tools generate synthetic data.
> **DataSynthX tells you if you can trust it — and why.**

---

## ⚡ Key Features

### 🔬 1. Statistical Profiling Engine

* Automatic detection:

  * Numeric, categorical, datetime columns
* Deep statistical extraction:

  * Mean, variance, skewness, kurtosis
  * Missing value patterns
  * Correlation matrix

---

### 🧬 2. Synthetic Data Generation Engine

* **Multivariate Gaussian modeling** (numeric)
* **Frequency-preserving sampling** (categorical)
* **Missing value replication**
* **Noise injection for realism**
* Scales to **hundreds of thousands of rows**

---

### 📊 3. Trust & Fidelity Metrics

* Correlation Preservation Score
* Distribution Similarity:

  * Kolmogorov-Smirnov Test
  * Wasserstein Distance
* Synthetic Consistency Index (SCI)

---

### 🤖 4. AI Insight Explainer (GAME CHANGER)

> This is what makes DataSynthX different.

* Interprets:

  * Statistical distributions
  * Correlation structures
  * Synthetic vs real differences
* Explains:

  * What changed
  * What stayed consistent
  * Whether the data is reliable
* Outputs:

  * Human-readable insights
  * Research-ready explanations

✅ No statistical expertise required
✅ Turns numbers into **understanding**

---

### 💳 5. Credit-Based Access System

* Google Sheets-powered backend
* Secure access keys (`DSX-XXXX-XXXX`)
* 1 generation = 1 credit
* Credits never expire

---

### 📤 6. Export Ready

* CSV download
* Excel download
* Ready for:

  * Research
  * ML pipelines
  * Testing environments

---

## 🧠 How It Works

```text
Upload Data → Profile → Generate → Validate → Explain → Export
```

### Step-by-step:

1. **Upload**

   * CSV / Excel dataset

2. **Profile**

   * Statistical structure extracted

3. **Generate**

   * Synthetic dataset created

4. **Validate**

   * Fidelity metrics computed

5. **Explain (AI Layer)**

   * AI interprets results
   * Highlights reliability + risks

6. **Export**

   * Download synthetic dataset

---

---

## 🧪 Core Components

### `DataProfiler`

Extracts full statistical structure from raw datasets.

### `SyntheticDataGenerator`

Generates synthetic data while preserving:

* Distributions
* Correlations
* Missing patterns

### `TrustMetrics`

Evaluates how “real” your synthetic data is.

### `AIExplainer`

Transforms metrics into:

* Insights
* Interpretations
* Decisions

---

## 🔐 Privacy by Design

* No raw data storage
* Synthetic output is non-identifiable
* Built for:

  * Compliance
  * Secure data sharing
  * Safe experimentation

---

## 💡 Use Cases

* 📊 Machine Learning training datasets
* 🧪 Academic & research simulations
* 🏥 Healthcare data (privacy-safe)
* 💳 Financial modeling
* 🔍 Data analysis without exposure
* 🧠 AI-assisted statistical interpretation

---

## 🛠️ Tech Stack

* **Frontend:** Streamlit
* **Backend:** Python
* **Data Processing:** Pandas, NumPy, SciPy
* **Visualization:** Plotly
* **Auth & Credits:** Google Sheets (gspread)
* **AI Engine:** OpenAI API

---

## ⚙️ Installation

```bash
git clone https://github.com/yourusername/datasynthx.git
cd datasynthx
pip install -r requirements.txt
```

---

## 🔑 Environment Setup

Create `.streamlit/secrets.toml`:

```toml
[gcp_service_account]
type = "service_account"
project_id = "..."
private_key = "..."
client_email = "..."

DSX_SHEET_ID = "your_sheet_id"
OPENAI_API_KEY = "your_openai_key"
```

---

## ▶️ Run Locally

```bash
streamlit run app.py
```

---

## 📈 Roadmap

* [ ] Differential Privacy Integration
* [ ] Time-Series Synthetic Data
* [ ] FastAPI API Access
* [ ] Batch Dataset Processing
* [ ] Team Collaboration Features
* [ ] Dataset Versioning

---

## 🤝 Contributing

Pull requests are welcome.
For major changes, open an issue first.

---

## 📩 Support

* Email: [Abdulwrite77@gmail.com](mailto:Abdulwrite77@gmail.com)
* WhatsApp: +2348096506034

---

## 📄 License

MIT License

---

## ⚡ Final Thought

> Data is not useful unless it is understood.

**DataSynthX doesn’t just generate data.
It makes data make sense.**
