# T12 Property Analysis Tool - Project Structure

## 📁 Complete Directory Organization

```
T12-Property-Analysis/
├── 📄 app.py                          # Main Streamlit application (entry point)
├── 📄 requirements.txt                # Python dependencies
├── 📄 .env                           # Environment variables (API keys)
├── 📄 README.md                      # Project documentation
├── 📄 IMPLEMENTATION_CHECKLIST.md    # Development progress tracking
├── 📄 PROJECT_STRUCTURE.md           # This documentation file
│
├── 📁 src/                           # Source code modules
│   ├── 📁 core/                      # Core business logic
│   │   ├── 📄 preprocess.py          # Data preprocessing and cleaning
│   │   ├── 📄 kpi_summary.py         # KPI calculation and summary generation
│   │   └── 📄 output_quality.py      # Output validation and quality control
│   │
│   ├── 📁 ai/                        # AI integration modules
│   │   ├── 📄 prompt.py              # Prompt engineering and templates
│   │   ├── 📄 assistants_api.py      # OpenAI Assistants API integration
│   │   └── 📄 model_config.py        # AI model configuration and settings
│   │
│   ├── 📁 ui/                        # User interface components
│   │   ├── 📄 validation.py          # File upload validation
│   │   ├── 📄 progress.py            # Progress tracking system
│   │   ├── 📄 data_analysis.py       # Data display and testing tools
│   │   ├── 📄 ai_analysis.py         # AI analysis interface
│   │   ├── 📄 reports.py             # Report generation and export
│   │   └── 📁 modes/                 # UI mode-specific components
│   │       ├── 📄 production_mode.py         # Entry point for production UI (delegates to modular components)
│   │       ├── 📄 production_mode_core.py    # Main orchestration for production mode
│   │       ├── 📄 production_sidebar.py      # Sidebar configuration for production mode
│   │       ├── 📄 production_upload.py       # File upload handling for production mode
│   │       ├── 📄 production_results.py      # Analysis display (structured + raw response) for production mode
│   │       ├── 📄 developer_mode.py          # Advanced debugging and settings interface (entry point)
│   │       ├── 📄 developer_mode_core.py     # Main orchestration for developer mode
│   │       ├── 📄 developer_sidebar.py       # Sidebar configuration for developer mode
│   │       ├── 📄 developer_upload.py        # File upload handling for developer mode
│   │       ├── 📄 developer_results.py       # Results display for developer mode
│   │       ├── 📄 developer_tools.py         # Developer tools and debug panels
│   │       └── 📄 mode_manager.py            # Mode switching and management
│   │
│   ├── 📁 export/                    # Report generation and export
│   │   ├── 📄 pdf_generator.py       # PDF report creation
│   │   ├── 📄 word_generator.py      # Word document export
│   │   └── 📄 report_templates.py    # Report formatting and templates
│   │
│   ├── 📁 automation/                # Weekly automation and batch processing
│   │   ├── 📄 weekly_processor.py    # Automated weekly report generation
│   │   ├── 📄 batch_handler.py       # Multi-property batch processing
│   │   └── 📄 historical_tracker.py  # Historical data comparison
│   │
│   └── 📁 settings/                  # Advanced settings and configuration
│       ├── 📄 template_manager.py    # Template editing and management
│       ├── 📄 config_editor.py       # Settings configuration interface
│       └── 📄 performance_tracker.py # Performance metrics and analytics
│
├── 📁 data/                          # Data storage
│   ├── 📄 Data.xlsx                  # Sample T12 data
│   ├── 📁 samples/                   # Sample T12 files for testing
│   ├── 📁 historical/                # Historical analysis data
│   └── 📁 templates/                 # Data processing templates
│
├── 📁 templates/                     # Report and UI templates
│   ├── 📁 pdf_templates/             # PDF report templates
│   ├── 📁 word_templates/            # Word document templates
│   └── 📁 ui_templates/              # UI component templates
│
├── 📁 config/                        # Configuration files
│   ├── 📄 property_profiles.json     # Property-specific configurations
│   ├── 📄 naming_conventions.json    # File and report naming rules
│   └── 📄 automation_settings.json   # Automation and scheduling settings
│
├── 📁 settings/                      # User settings and preferences
│   ├── 📄 user_preferences.json      # UI mode, default settings
│   ├── 📄 prompt_templates.json      # Custom prompt templates
│   └── 📄 model_configurations.json  # AI model settings
│
├── 📁 outputs/                       # Generated reports and exports
│   ├── 📁 pdf_reports/               # Generated PDF reports
│   ├── 📁 word_reports/              # Generated Word documents
│   └── 📁 analysis_logs/             # Analysis history and logs
│
├── 📁 backups/                       # Settings and template backups
│   ├── 📁 settings_backup/           # Versioned settings backups
│   └── 📁 template_backup/           # Template version history
│
├── 📁 logs/                          # Application and API logs
│   ├── � app_logs/                  # Application runtime logs
│   ├── 📁 api_logs/                  # OpenAI API call logs
│   └── 📁 performance_logs/          # Performance and usage metrics
│
├── 📁 tests/                         # Test files and validation
│   ├── 📄 test_api_mock.py           # API testing with mocks
│   ├── 📄 test_output_consistency.py # Output quality testing
│   ├── 📁 unit_tests/                # Unit tests for individual modules
│   ├── 📁 integration_tests/         # End-to-end workflow tests
│   └── 📁 sample_data/               # Test data and validation files
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
- **`model_config.py`**: AI model configuration, parameters, and settings management

### **User Interface** (`src/ui/`)
- **`validation.py`**: File upload validation and error handling
- **`progress.py`**: Progress tracking system for multi-step workflows
- **`data_analysis.py`**: Data visualization and debugging tools
- **`ai_analysis.py`**: AI analysis interface with Enhanced/Standard options
- **`reports.py`**: PDF, Word, and text report generation
- **`modes/production_mode.py`**: Entry point for production UI (delegates to modular components)
- **`modes/production_mode_core.py`**: Main orchestration for production mode
- **`modes/production_sidebar.py`**: Sidebar configuration for production mode
- **`modes/production_upload.py`**: File upload handling for production mode
- **`modes/production_results.py`**: Analysis display (structured + raw response) for production mode
- **`modes/developer_mode.py`**: Entry point for developer UI (delegates to modular components)
- **`modes/developer_mode_core.py`**: Main orchestration for developer mode
- **`modes/developer_sidebar.py`**: Sidebar configuration for developer mode
- **`modes/developer_upload.py`**: File upload handling for developer mode
- **`modes/developer_results.py`**: Results display for developer mode
- **`modes/developer_tools.py`**: Developer tools and debug panels
- **`modes/mode_manager.py`**: Mode switching and management

### **Export & Reports** (`src/export/`)
- **`pdf_generator.py`**: Professional PDF report creation with templates
- **`word_generator.py`**: Word document export with custom formatting
- **`report_templates.py`**: Template management and report formatting

### **Automation** (`src/automation/`)
- **`weekly_processor.py`**: Automated weekly report generation
- **`batch_handler.py`**: Multi-property batch processing capabilities
- **`historical_tracker.py`**: Historical data comparison and trend analysis

### **Settings & Configuration** (`src/settings/`)
- **`template_manager.py`**: Template editing and management interface
- **`config_editor.py`**: Settings configuration and customization
- **`performance_tracker.py`**: Performance metrics, analytics, and optimization

### **Data Storage**
- **`data/`**: Sample files, historical data, and processing templates
- **`templates/`**: Report templates and UI customization files
- **`config/`**: Property profiles, naming conventions, and automation settings
- **`settings/`**: User preferences, custom templates, and model configurations
- **`outputs/`**: Generated reports, analysis logs, and exported documents
- **`backups/`**: Version control for settings and templates
- **`logs/`**: Application logs, API monitoring, and performance tracking

### **Tests** (`tests/`)
- **`test_api_mock.py`**: Mock API testing for development
- **`test_output_consistency.py`**: Quality assurance testing
- **`unit_tests/`**: Individual module testing
- **`integration_tests/`**: End-to-end workflow validation
- **`sample_data/`**: Test data and validation files

## 🚀 Quick Start

1. **Main Entry Point**: Run `streamlit run app.py`
2. **Core Logic**: Business logic is in `src/core/`
3. **UI Components**: All Streamlit UI code is in `src/ui/`
4. **AI Features**: AI integration is in `src/ai/`

## 📋 File Dependencies

### **Main Application Flow**
```
app.py
├── src/ui/validation.py
├── src/ui/progress.py
├── src/ui/modes/production_mode.py     # Production UI mode
├── src/ui/modes/developer_mode.py      # Developer UI mode
└── src/core/kpi_summary.py
```

### **AI Analysis Pipeline**
```
src/ui/ai_analysis.py
├── src/ai/prompt.py                    # Standard Analysis
├── src/ai/assistants_api.py            # Enhanced Analysis
└── src/ai/model_config.py              # Model settings

src/ai/assistants_api.py
└── src/core/preprocess.py              # Raw data upload

src/core/kpi_summary.py
└── src/core/preprocess.py              # Data processing
```

### **Export & Reports**
```
src/ui/reports.py
├── src/export/pdf_generator.py
├── src/export/word_generator.py
└── src/export/report_templates.py

src/export/pdf_generator.py
└── templates/pdf_templates/            # Template files

src/export/word_generator.py
└── templates/word_templates/           # Template files
```

### **Developer Mode Dependencies**
```
src/ui/modes/developer_mode.py
├── src/ui/data_analysis.py             # Debug tools
├── src/settings/template_manager.py    # Template editing
├── src/settings/config_editor.py       # Settings management
├── src/settings/performance_tracker.py # Analytics
└── logs/                              # Log monitoring
```

### **Automation & Batch Processing**
```
src/automation/weekly_processor.py
├── src/core/preprocess.py
├── src/core/kpi_summary.py
├── src/ai/assistants_api.py
└── src/export/pdf_generator.py

src/automation/batch_handler.py
├── src/automation/weekly_processor.py
└── config/property_profiles.json

src/automation/historical_tracker.py
└── data/historical/                   # Historical data storage
```

## 🎯 Implementation Phases

### **Phase 1: Current Structure (✅ Complete)**
- Basic modular architecture with `src/core/`, `src/ai/`, `src/ui/`
- Working Enhanced and Standard analysis
- File upload, validation, and basic export

### **Phase 2: UI Mode System (🔄 In Progress)**
- Implement `src/ui/modes/` with production and developer views
- Add mode toggle in sidebar
- Optimize layout for each mode

### **Phase 3: Advanced Features (📋 Planned)**
- Create `src/export/`, `src/automation/`, `src/settings/` modules
- Implement template management and customization
- Add performance tracking and analytics

### **Phase 4: Production Ready (🚀 Future)**
- Complete folder structure with all storage directories
- Backup systems and version control
- Desktop application packaging

## 🔧 Development Guidelines

1. **Follow the structure**: Create files in their designated directories
2. **Maintain dependencies**: Update this file when adding new modules
3. **Use consistent naming**: Follow the established patterns
4. **Document changes**: Update both this file and the implementation checklist
5. **Test incrementally**: Validate each module as it's created

## 📝 Structure Validation Checklist

- [ ] All `src/` modules are properly organized by function
- [ ] Data storage directories exist and are organized
- [ ] Configuration files are separated from code
- [ ] Templates and outputs have dedicated folders
- [ ] Backup and logging systems are in place
- [ ] Test files mirror the source structure
- [ ] Documentation is complete and up-to-date
