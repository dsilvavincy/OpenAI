# 🏢 T12 Property Analysis Tool

An AI-powered Streamlit application for analyzing commercial real estate T12 (Trailing Twelve Months) financial data.

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Up Environment**
   ```bash
   # Create .env file with your OpenAI API key
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```

3. **Run Application**
   ```bash
   streamlit run app.py
   ```

4. **Open Browser**
   Navigate to `http://localhost:8501`

## 📁 Project Structure

```
T12-Property-Analysis/
├── 📄 app.py                    # Main Streamlit application
├── 📄 requirements.txt          # Python dependencies
├── 📄 .env                     # Environment variables
│
├── 📁 src/                     # Source code modules
│   ├── 📁 core/                # Core business logic
│   │   ├── 📄 preprocess.py    # Data preprocessing
│   │   ├── 📄 kpi_summary.py   # KPI calculations
│   │   └── 📄 output_quality.py # Quality control
│   │
│   ├── 📁 ai/                  # AI integration
│   │   ├── 📄 prompt.py        # OpenAI API calls
│   │   └── 📄 assistants_api.py # Enhanced AI analysis
│   │
│   └── 📁 ui/                  # User interface
│       ├── 📄 validation.py    # File validation
│       ├── 📄 progress.py      # Progress tracking
│       ├── 📄 data_analysis.py # Data visualization
│       ├── 📄 ai_analysis.py   # AI analysis UI
│       └── 📄 reports.py       # Report generation
│
├── 📁 tests/                   # Test files
├── 📁 data/                    # Sample data files
└── 📁 docs/                    # Documentation
```

## ✨ Features

### 🔍 **Data Analysis**
- T12 Excel file validation and processing
- Automated data cleaning and standardization
- YTD vs Monthly data handling
- KPI calculation and summary generation

### 🤖 **AI-Powered Insights**
- **Standard Analysis**: Text-based KPI summary analysis
- **Enhanced Analysis**: Raw data analysis using OpenAI Assistants API
- Automated property performance insights
- Investment recommendations

### 📊 **Reporting**
- PDF report generation
- Word document export
- Text-based summaries
- Professional formatting

### 🎛️ **User Interface**
- Intuitive Streamlit web interface
- Progress tracking for long operations
- Data debugging and validation tools
- Real-time analysis feedback

## 🔧 Technical Details

### **Core Technologies**
- **Python 3.8+**: Main programming language
- **Streamlit**: Web application framework
- **Pandas**: Data processing and analysis
- **OpenAI API**: AI-powered analysis
- **ReportLab**: PDF generation
- **python-docx**: Word document generation

### **Architecture**
- **Modular Design**: Clean separation of concerns
- **Type Safety**: Comprehensive type hints
- **Error Handling**: Robust error management
- **Testing**: Unit tests for critical functions

## 📋 Usage Guide

### **Step 1: Upload Data**
- Upload your T12 Excel file
- System validates file format and size
- Automatic data preprocessing begins

### **Step 2: Review Data**
- View data analysis and debugging tools
- Verify KPI calculations
- Test different analysis parameters

### **Step 3: Generate Analysis**
- Choose between Standard or Enhanced analysis
- Enhanced analysis provides deeper insights using raw data
- Standard analysis uses text-based KPI summaries

### **Step 4: Export Results**
- Generate professional PDF reports
- Export to Word documents
- Save text summaries

## 🛠️ Development

### **Adding New Features**
1. **UI Components**: Add to `src/ui/`
2. **Business Logic**: Add to `src/core/`
3. **AI Features**: Add to `src/ai/`
4. **Tests**: Add to `tests/`

### **File Organization Rules**
- **Core Logic**: Business logic, data processing, calculations
- **AI Integration**: OpenAI API, prompt engineering, AI analysis
- **UI Components**: Streamlit interfaces, user interactions
- **Tests**: Unit tests, integration tests, mocks

### **Best Practices**
- Use type hints for all functions
- Add comprehensive docstrings
- Write unit tests for new features
- Follow PEP 8 coding standards

## 🚨 Troubleshooting

### **Common Issues**
1. **API Key Errors**: Verify your OpenAI API key in `.env`
2. **File Upload Issues**: Check file format (Excel) and size (<50MB)
3. **Memory Issues**: Large files may require more RAM
4. **Import Errors**: Run `pip install -r requirements.txt`

### **Getting Help**
- Check the `PROJECT_STRUCTURE.md` for detailed module descriptions
- Review test files for usage examples
- Examine existing code for patterns and conventions

## 📈 Roadmap

- [ ] Support for additional file formats (CSV, JSON)
- [ ] Advanced data visualization
- [ ] Multi-property comparison
- [ ] Historical trend analysis
- [ ] Custom KPI definitions
- [ ] API integration for data sources

## 📄 License

[Add your license information here]

## 🤝 Contributing

[Add contribution guidelines here]
