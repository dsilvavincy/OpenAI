# AI-Driven T12 Data Question Generator

## Implementation, Testing & Validation Roadmap

Use this checklist to track progress through each stage. Mark each box as you complete the step.

---

### 1. Project Setup
- [x] Scaffold project structure and modules
- [x] Install dependencies (`pandas`, `openai`, `streamlit`, `openpyxl`)
- [x] Set up OpenAI API key using a `.env` file (recommended) or environment variable
- [x] Create sample T12 Excel template for testing
**✅ VALIDATION REQUIRED**: All dependencies installed, sample T12 file created, API key configured via `.env` or environment variable

### 2. T12 Data Format Standardization
- [x] Define standard T12 Excel structure (columns, headers, sheet names)
- [x] Document expected data format and validation rules
- [x] Create data validation checks for uploaded files
- [x] Handle common T12 format variations and edge cases
**✅ VALIDATION REQUIRED**: Process multiple T12 formats successfully, validation catches errors

### 3. Data Ingestion & Preprocessing
- [x] Implement `tidy_sheet_all()` to clean and reshape T12 Excel data
- [x] Add robust error handling for malformed Excel files
- [x] Test with multiple sample T12 Excel files
- [x] Validate output DataFrame structure and content
- [x] Implement data quality checks (missing values, invalid dates, etc.)
**✅ VALIDATION REQUIRED**: Clean data output, proper error handling, consistent DataFrame structure

### 4. KPI Summary Generation
- [x] Implement `generate_kpi_summary()` to extract and summarize KPIs
- [x] Define standard KPI calculations (Revenue, NOI, Occupancy, etc.)
- [x] Add trend analysis (month-over-month, year-over-year)
- [x] Test summary output for accuracy and clarity
- [x] Validate bullet-point formatting for LLM input
**✅ VALIDATION REQUIRED**: Accurate KPI calculations, professional summary format, proper trend analysis

### 5. Standardized AI Prompt Engineering
- [x] Create comprehensive system prompt template for T12 analysis
- [x] Define standard analysis categories (financial performance, trends, red flags)
- [x] Implement prompt templates for consistent question generation
- [x] Add context about real estate industry standards and benchmarks
- [x] Test prompt variations for output quality and consistency
- [x] Create fallback prompts for edge cases
**✅ VALIDATION REQUIRED**: Consistent AI outputs, professional analysis quality, standardized question format

### 6. OpenAI API Integration
- [x] Implement `call_openai()` to send prompt and receive response
- [x] Add retry logic and rate limiting for API calls
- [x] Implement response validation and quality checks
- [x] Test with sample data and check API output consistency
- [x] Handle API errors and edge cases gracefully
- [x] Add logging for API calls and responses
**✅ VALIDATION REQUIRED**: Successful API calls, proper error handling, consistent response quality

### 7. Output Standardization & Quality Control
- [x] Define standard output format for AI-generated insights
- [x] Implement output validation (structure, completeness, relevance)
- [x] Create quality scoring system for AI responses
- [x] Add output post-processing and formatting
- [x] Test output consistency across multiple runs
**✅ VALIDATION REQUIRED**: Consistent output format, quality validation working, professional presentation

### 8. User Interface (UI) Development - Dual Mode System
- [x] Add Streamlit to requirements
- [x] Build Streamlit UI for Excel file upload, processing, output display, and export
- [x] Add progress indicators for long-running processes
- [x] Implement file validation feedback in UI
- [x] Add OpenAI API key input field (secure)
- [x] Ensure all user interactions and outputs are handled via the UI (no console interaction)
- [x] Test UI for usability and error handling
- [ ] **Production Mode**: Clean, minimal UI focused on upload → progress → results → export workflow
- [ ] **Developer Mode**: Toggle to show advanced features (prompt testing, raw data, debug info, settings)
- [ ] **Mode Toggle**: Easy switch between Production and Developer modes in sidebar
- [ ] **Settings Panel**: Developer mode includes prompt templates, model settings, validation controls
- [ ] **Layout Optimization**: Production mode maximizes space for analysis results and export options
- [ ] **User Preference**: Remember last selected mode in session state
- [ ] **Project Structure**: Create `src/ui/modes/` folder with `production_mode.py` and `developer_mode.py` components
- [ ] **UI Components**: Organize mode-specific UI elements in respective files with clear imports
**✅ VALIDATION REQUIRED**: Both modes work seamlessly, production mode is clean and professional, developer mode has all debugging tools

### 9. **PRIORITY: AI Analysis Quality & Output Validation**
- [x] **Test with real T12 data**: Upload actual T12 file and validate DataFrame structure
- [x] **Debug data quality issues**: Fix MonthParsed and other data parsing problems
- [ ] **Validate KPI calculations**: Ensure accurate financial metrics (Revenue, NOI, Occupancy)
- [ ] **Test OpenAI API calls**: Send KPI summary to OpenAI and validate response quality
- [x] **Analyze AI output quality**: Review strategic questions, recommendations, and trends
- [x] **Iterate on prompts**: Improve prompts based on actual AI responses - Added UI prompt preview!
- [ ] **Test multiple T12 files**: Validate consistency across different property data
- [x] **Display analysis results**: Ensure all AI output is properly shown in UI

### 10. **Hybrid Assistants API Implementation** 
- [x] **HYBRID ARCHITECTURE**: Keep local preprocessing AND send raw data to OpenAI
- [x] Refactor workflow to use OpenAI Assistants API with code_interpreter tool
- [x] Upload processed CSV/Excel to OpenAI and manage file_ids
- [x] Send BOTH KPI summary (from local preprocessing) AND raw dataset to OpenAI
- [x] Design enhanced prompts that leverage both structured summary and raw data access
- [ ] Handle multi-part outputs (text, plots, downloadable files)
- [x] Validate LLM Python analysis and outputs for accuracy and completeness
- [x] Update UI to support file upload and display of code_interpreter results
- [x] **Fix Enhanced Analysis validation**: Updated validation logic for Assistants API responses
- [x] **SUCCESSFULLY TESTED**: Enhanced Analysis with raw data access is working perfectly!
- [ ] Test with large and multi-property datasets

### 11. Report Generation & Export
- [x] Display all AI-generated output in the application UI
- [x] Implement export to PDF with professional formatting
- [x] Add Word document export option
- [x] Create standardized report template
- [x] Add date/timestamp and property information to reports
- [ ] Test export functionality across different formats
- [ ] **Project Structure**: Create `src/export/` folder with `pdf_generator.py`, `word_generator.py`, and `report_templates.py`
- [ ] **Template Storage**: Create `templates/` folder with customizable report templates (HTML, CSS, Word styles)
- [ ] **Output Management**: Create `outputs/` folder structure for generated reports with proper naming conventions

### 12. Weekly Automation & Standardization
- [ ] Create template system for consistent weekly reports
- [ ] Add property metadata tracking (name, address, portfolio info)
- [ ] Implement historical comparison features
- [ ] Add batch processing for multiple properties
- [ ] Create standardized naming conventions for files and reports
- [ ] Test weekly workflow simulation
- [ ] **Project Structure**: Create `src/automation/` folder with `weekly_processor.py`, `batch_handler.py`, and `historical_tracker.py`
- [ ] **Data Storage**: Create `data/historical/` and `data/templates/` folders for storing past analyses and templates
- [ ] **Configuration Files**: Create `config/` folder with property profiles, naming conventions, and automation settings

### 13. Advanced Settings & Template Management (Developer Mode)
- [ ] **Prompt Template Editor**: UI to customize system and user prompts for both Standard and Enhanced analysis
- [ ] **Model Configuration**: Settings for OpenAI model selection, temperature, max tokens, etc.
- [ ] **Validation Rules**: Customizable validation criteria for AI responses
- [ ] **KPI Template System**: Editable templates for different property types or analysis focuses
- [ ] **Export Templates**: Customizable PDF/Word report templates with branding options
- [ ] **Debug Console**: Real-time logging and API call monitoring in developer mode
- [ ] **A/B Testing**: Compare different prompt versions and track performance metrics
- [ ] **Backup/Restore**: Save and load custom settings and templates
- [ ] **Performance Metrics**: Track token usage, response times, and analysis quality scores
- [ ] **Advanced Filters**: Developer controls for data preprocessing and analysis scope
- [ ] **Project Structure**: Create `src/settings/` folder with `template_manager.py`, `config_editor.py`, and `performance_tracker.py`
- [ ] **Settings Storage**: Create `settings/` folder with JSON files for user preferences, templates, and configurations
- [ ] **Backup System**: Create `backups/` folder with versioned settings and template snapshots
**✅ VALIDATION REQUIRED**: All settings persist correctly, templates are editable and apply properly, performance tracking works

### 14. Desktop Application Packaging
- [ ] Package Streamlit app as a standalone desktop executable using PyInstaller
- [ ] Include all dependencies and assets in executable
- [ ] Test packaged app on target desktop environment
- [ ] Create installer with proper file associations
- [ ] Document installation and usage instructions
- [ ] Test offline functionality (except OpenAI API calls)

**✅ VALIDATION REQUIRED**: LLM can analyze full dataset via code_interpreter, outputs are accurate, and UI supports new workflow

---

**🚨 CRITICAL DEVELOPMENT RULES:**
1. **SEQUENTIAL EXECUTION ONLY**: Work on checklist items in exact order - no skipping or parallel work
2. **VALIDATION REQUIRED**: Each stage must pass validation requirements before proceeding
3. **CHECKLIST UPDATES**: Mark [x] only after successful testing and validation
4. **NO SHORTCUTS**: Every item must be properly implemented and tested
5. **STAGE GATES**: Complete entire stage before moving to next stage

**Current Status Check:**
- **Next Task**: Look for first [ ] (uncompleted) item in checklist
- **Validation**: Ensure all [x] items actually work as specified
- **Testing**: Use real T12 data for validation, not mock data

**Critical Success Factors:**
- **Standardization**: T12 format consistency and standardized AI prompts are essential for reliable weekly reports
- **Quality Control**: Implement validation at every step to ensure accurate and relevant AI outputs
- **User Experience**: All interactions must be UI-based for a professional desktop application
- **Automation**: Design for weekly repetition with minimal user intervention
- **Error Handling**: Robust error handling for real-world data variations and edge cases

**Weekly Workflow Requirements:**
1. Upload T12 Excel file via UI
2. Automatic data validation and preprocessing
3. Generate standardized KPI summary
4. Apply consistent AI prompts for analysis
5. Produce formatted report with insights and recommendations
6. Export professional PDF/Word report with timestamp and property details

**📁 For complete project structure details, see `PROJECT_STRUCTURE.md`**
