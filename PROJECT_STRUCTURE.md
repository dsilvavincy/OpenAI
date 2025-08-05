# T12 Property Analysis Tool - Project Structure

## 📁 Directory Organization

```
T12-Property-Analysis/
├── 📄 app.py                          # Main Streamlit application (entry point)
├── 📄 requirements.txt                # Python dependencies
├── 📄 .env                           # Environment variables (API keys)
├── 📄 PROJECT_STRUCTURE.md           # This documentation file
├── 📄 IMPLEMENTATION_CHECKLIST.md    # Development progress tracking
│
├── 📁 src/                           # Source code modules
│   ├── 📁 core/                      # Core business logic
│   │   ├── 📄 preprocess.py          # Data preprocessing and cleaning
│   │   ├── 📄 kpi_summary.py         # KPI calculation and summary generation
│   │   └── 📄 output_quality.py      # Output validation and quality control
│   │
│   ├── 📁 ai/                        # AI-related functionality
│   │   ├── 📄 prompt.py              # OpenAI prompt engineering and API calls
│   │   └── 📄 assistants_api.py      # Enhanced AI analysis using Assistants API
│   │
│   ├── 📁 ui/                        # User interface components
│   │   ├── 📄 validation.py          # File upload validation
│   │   ├── 📄 progress.py            # Progress tracking system
│   │   ├── 📄 data_analysis.py       # Data analysis and debugging UI
│   │   ├── 📄 ai_analysis.py         # AI analysis interface
│   │   └── 📄 reports.py             # Report generation and export
│   │
│   └── 📁 utils/                     # Utility functions
│       └── 📄 __init__.py            # Package initialization
│
├── 📁 tests/                         # Test files
│   ├── 📄 test_api_mock.py           # API testing with mocks
│   └── 📄 test_output_consistency.py # Output quality testing
│
├── 📁 data/                          # Data files
│   ├── 📄 Data.xlsx                  # Sample T12 data
│   └── 📄 temp_Data.xlsx             # Temporary data files
│
└── 📁 docs/                          # Documentation
    ├── 📄 README.md                  # Project overview and setup
    ├── 📄 USER_GUIDE.md              # How to use the application
    └── 📄 DEVELOPMENT.md             # Development guidelines
```

## 🔧 Module Descriptions

### **Core Business Logic** (`src/core/`)
- **`preprocess.py`**: Handles Excel file parsing, data cleaning, and T12 format standardization
- **`kpi_summary.py`**: Calculates key performance indicators and generates text summaries
- **`output_quality.py`**: Validates AI responses and ensures output quality

### **AI Integration** (`src/ai/`)
- **`prompt.py`**: Manages OpenAI API calls, prompt engineering, and standard analysis
- **`assistants_api.py`**: Enhanced AI analysis using OpenAI Assistants API with raw data access

### **User Interface** (`src/ui/`)
- **`validation.py`**: File upload validation and error handling
- **`progress.py`**: Progress tracking system for multi-step workflows
- **`data_analysis.py`**: Data visualization and debugging tools
- **`ai_analysis.py`**: AI analysis interface with Enhanced/Standard options
- **`reports.py`**: PDF, Word, and text report generation

### **Tests** (`tests/`)
- **`test_api_mock.py`**: Mock API testing for development
- **`test_output_consistency.py`**: Quality assurance testing

### **Data** (`data/`)
- Sample files and temporary data storage

## 🚀 Quick Start

1. **Main Entry Point**: Run `streamlit run app.py`
2. **Core Logic**: Business logic is in `src/core/`
3. **UI Components**: All Streamlit UI code is in `src/ui/`
4. **AI Features**: AI integration is in `src/ai/`

## 📋 File Dependencies

```
app.py
├── src/ui/validation.py
├── src/ui/progress.py
├── src/ui/data_analysis.py
├── src/ui/ai_analysis.py
├── src/ui/reports.py
└── src/core/kpi_summary.py

src/ui/ai_analysis.py
├── src/ai/prompt.py
└── src/ai/assistants_api.py

src/core/kpi_summary.py
└── src/core/preprocess.py
```

## 🎯 Next Steps for Better Organization

1. **Reorganize existing files** into the new structure
2. **Create missing documentation** files
3. **Add package initialization** files
4. **Implement consistent naming** conventions
5. **Add type hints** and docstrings
