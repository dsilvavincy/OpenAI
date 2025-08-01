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
- [ ] Test summary output for accuracy and clarity
- [ ] Validate bullet-point formatting for LLM input
**✅ VALIDATION REQUIRED**: Accurate KPI calculations, professional summary format, proper trend analysis

### 5. Standardized AI Prompt Engineering
- [x] Create comprehensive system prompt template for T12 analysis
- [x] Define standard analysis categories (financial performance, trends, red flags)
- [x] Implement prompt templates for consistent question generation
- [x] Add context about real estate industry standards and benchmarks
- [ ] Test prompt variations for output quality and consistency
- [ ] Create fallback prompts for edge cases
**✅ VALIDATION REQUIRED**: Consistent AI outputs, professional analysis quality, standardized question format

### 6. OpenAI API Integration
- [x] Implement `call_openai()` to send prompt and receive response
- [x] Add retry logic and rate limiting for API calls
- [x] Implement response validation and quality checks
- [ ] Test with sample data and check API output consistency
- [ ] Handle API errors and edge cases gracefully
- [ ] Add logging for API calls and responses
**✅ VALIDATION REQUIRED**: Successful API calls, proper error handling, consistent response quality

### 7. Output Standardization & Quality Control
- [ ] Define standard output format for AI-generated insights
- [ ] Implement output validation (structure, completeness, relevance)
- [ ] Create quality scoring system for AI responses
- [ ] Add output post-processing and formatting
- [ ] Test output consistency across multiple runs
**✅ VALIDATION REQUIRED**: Consistent output format, quality validation working, professional presentation

### 8. User Interface (UI) Development
- [x] Add Streamlit to requirements
- [x] Build Streamlit UI for Excel file upload, processing, output display, and export
- [ ] Add progress indicators for long-running processes
- [ ] Implement file validation feedback in UI
- [ ] Add OpenAI API key input field (secure)
- [ ] Ensure all user interactions and outputs are handled via the UI (no console interaction)
- [ ] Test UI for usability and error handling
**✅ VALIDATION REQUIRED**: Complete UI workflow, no console dependencies, professional interface, proper error handling

### 9. Report Generation & Export
- [ ] Display all AI-generated output in the application UI
- [ ] Implement export to PDF with professional formatting
- [ ] Add Word document export option
- [ ] Create standardized report template
- [ ] Add date/timestamp and property information to reports
- [ ] Test export functionality across different formats

### 10. Weekly Automation & Standardization
- [ ] Create template system for consistent weekly reports
- [ ] Add property metadata tracking (name, address, portfolio info)
- [ ] Implement historical comparison features
- [ ] Add batch processing for multiple properties
- [ ] Create standardized naming conventions for files and reports
- [ ] Test weekly workflow simulation

### 11. Desktop Application Packaging
- [ ] Package Streamlit app as a standalone desktop executable using PyInstaller
- [ ] Include all dependencies and assets in executable
- [ ] Test packaged app on target desktop environment
- [ ] Create installer with proper file associations
- [ ] Document installation and usage instructions
- [ ] Test offline functionality (except OpenAI API calls)

### 12. End-to-End Validation
- [ ] Run full workflow with real T12 data from multiple properties
- [ ] Validate AI-generated questions and insights for relevance and accuracy
- [ ] Test consistency across multiple weeks of data
- [ ] Conduct user acceptance testing
- [ ] Review and refine based on feedback
- [ ] Performance testing with large datasets

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
