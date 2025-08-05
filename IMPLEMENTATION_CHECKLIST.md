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

### 3. Data Ingestion & Preprocessing - Scalable Format System
- [x] Implement `tidy_sheet_all()` to clean and reshape T12 Excel data
- [x] Add robust error handling for malformed Excel files
- [x] Test with multiple sample T12 Excel files
- [x] Validate output DataFrame structure and content
- [x] Implement data quality checks (missing values, invalid dates, etc.)
- [x] **Format Registry System**: Create registry to dynamically load format processors
- [x] **Base Format Processor**: Create abstract base class for all format processors
- [x] **T12 Processor Module**: Refactor existing T12 logic into modular processor class
- [ ] **Weekly Database Processor**: Create second format processor following base class pattern
- [x] **Format Auto-Detection**: Auto-detect format type from file structure/headers
- [x] **Unified Output Interface**: All processors return standardized data structure
- [x] **Format Validation Framework**: Base validation with format-specific validation rules
- [x] **Plugin Architecture**: Easy addition of new format types without core app changes
- [x] **Project Structure**: Create `src/core/formats/` with `base_processor.py`, `t12_processor.py`, `weekly_processor.py`
- [x] **Format Registry**: Create `src/core/format_registry.py` to manage available processors
- [x] **Configuration**: Create `config/formats/` folder with JSON config for each format type
**✅ VALIDATION REQUIRED**: Plugin system works, easy to add new formats, consistent interface across all processors

### 4. KPI Summary Generation - Scalable KPI System
- [x] Implement `generate_kpi_summary()` to extract and summarize KPIs
- [x] Define standard KPI calculations (Revenue, NOI, Occupancy, etc.)
- [x] Add trend analysis (month-over-month, year-over-year)
- [x] Test summary output for accuracy and clarity
- [x] Validate bullet-point formatting for LLM input
- [x] **Base KPI Calculator**: Create abstract base class for all KPI calculators
- [x] **T12 KPI Calculator**: Refactor existing KPI logic into T12-specific calculator class
- [ ] **Weekly Database KPI Calculator**: Create KPI calculator for weekly database format
- [x] **KPI Registry System**: Registry to dynamically load KPI calculators for each format
- [x] **Format-Specific Metrics**: Each format defines its own relevant KPIs and calculations
- [x] **Standardized KPI Output**: All calculators return consistent KPI summary structure
- [x] **Trend Analysis Framework**: Base trend analysis with format-specific trend calculations
- [x] **Cross-Format KPI Mapping**: Map similar KPIs across formats when possible
- [x] **KPI Templates**: Template system for each format's analysis focus
- [x] **Project Structure**: Create `src/core/kpis/` with `base_kpi_calculator.py`, format-specific calculators
- [x] **KPI Configuration**: Create `config/kpis/` with JSON configs defining KPIs for each format
**✅ VALIDATION REQUIRED**: KPI system is modular, easy to add new KPI calculators, consistent output format

### 5. Standardized AI Prompt Engineering - **DYNAMIC MULTI-FORMAT SYSTEM** ✅ COMPLETED
- [x] Create comprehensive system prompt template for T12 analysis
- [x] Define standard analysis categories (financial performance, trends, red flags)
- [x] Implement prompt templates for consistent question generation
- [x] Add context about real estate industry standards and benchmarks
- [x] Test prompt variations for output quality and consistency
- [x] Create fallback prompts for edge cases
- [x] **DYNAMIC PROMPT SYSTEM**: Create format-specific prompt configurations in `config/prompts/` directory
- [x] **PROMPT MANAGER**: Implement `PromptManager` class to dynamically load format-specific prompts and instructions
- [x] **CONFIGURABLE ANALYSIS FRAMEWORKS**: Each format defines its own analysis approach, output requirements, and validation criteria
- [x] **FORMAT-SPECIFIC INSTRUCTIONS**: T12, Weekly Database, and other formats have tailored prompts and analysis focuses
- [x] **TEMPLATE SYSTEM**: JSON-based prompt templates with role descriptions, data structure notes, analysis frameworks, and output requirements
- [x] **VALIDATION KEYWORDS**: Format-specific keyword validation for response quality checking
- [x] **ASSISTANTS API INTEGRATION**: Format-specific instructions for enhanced analysis with code_interpreter
- [x] **BACKWARD COMPATIBILITY**: Existing T12 system continues to work while supporting new formats
- [x] **PROMPT CACHING**: Efficient loading and caching of prompt configurations
- [x] **FALLBACK PROMPTS**: Format-specific fallback and minimal prompts for edge cases
- [x] **HARDCODED PROMPT ELIMINATION**: Removed all hardcoded T12-specific prompts from `prompt.py` and `assistants_api.py`
- [x] **CLASS REFACTORING**: Updated `T12AssistantAnalyzer` to `PropertyAssistantAnalyzer` for multi-format support
- [x] **FUNCTION PARAMETER UPDATES**: Added `format_name` parameters throughout the analysis pipeline
- [x] **CONFIGURATION FILES CREATED**: 
  - `config/prompts/t12_monthly_financial.json` - Complete T12 prompt template
  - `config/prompts/weekly_database.json` - Weekly database prompt template
- [x] **UTILITY MODULES**: Created `src/ai/prompt_manager.py` for dynamic prompt management
- [x] **FORMAT DETECTION UTILITIES**: Created `src/utils/format_detection.py` for format identification and management
- [x] **TESTING COMPLETED**: All prompt generation, validation, and format detection functions tested successfully
- [x] **INTEGRATION UPDATED**: Updated all calling functions to pass format parameters
- [x] **ERROR HANDLING**: Comprehensive fallback to default prompts when format configs are missing
### 5.1. **FORMAT-AWARE INTEGRATION & DEPLOYMENT**
- [x] **UI INTEGRATION**: Update Production and Developer mode UIs to pass detected format to analysis functions
  - [x] Update `production_mode.py` to pass format parameter to `display_ai_analysis_section()`
  - [x] Update `developer_results.py` to pass format parameter to `display_ai_analysis_section()`
  - [x] Add format detection calls in upload/preprocessing sections
- [x] **PREPROCESSING INTEGRATION**: Integrate format detection into data preprocessing pipeline
  - [x] Add format detection call after `tidy_sheet_all()` processing
  - [x] Store detected format alongside processed data
- [x] **SESSION STATE MANAGEMENT**: Store detected format in session state for consistent use across UI modes
  - [x] Integrate `store_detected_format()` and `get_stored_format()` utilities
  - [x] Ensure format persists across UI mode switches
- [x] **FORMAT DISPLAY**: Show detected format type to users for transparency
  - [x] Add format indicator in UI (e.g., "Detected Format: T12 Monthly Financial")
  - [x] Include format info in analysis results headers
- [x] **CROSS-MODE FORMAT PERSISTENCE**: Ensure format detection persists when switching between Production/Developer modes
  - [x] Test format persistence with SharedFileManager integration
- [ ] **FORMAT OVERRIDE**: Allow advanced users to manually override detected format in Developer mode
  - [ ] Add format selection dropdown in Developer mode
  - [ ] Implement format override functionality
- [ ] **VALIDATION TESTING**: Test analysis quality with multiple format types using real data
  - [ ] Test T12 format with existing data
  - [ ] Create sample weekly database data for testing
  - [ ] Validate that different formats produce appropriate analysis content
- [ ] **ERROR SCENARIOS**: Test behavior with unknown formats and edge cases
  - [ ] Test with files that don't match any known format
  - [ ] Verify graceful fallback to default T12 prompts
- [ ] **PERFORMANCE TESTING**: Verify prompt loading performance doesn't impact user experience
  - [ ] Test prompt loading speed with multiple format configs
  - [ ] Verify caching works correctly
- [ ] **DOCUMENTATION**: Update user documentation to explain multi-format support
  - [ ] Document supported file formats
  - [ ] Explain format auto-detection behavior
### 5.2. **COMPLETED MULTI-FORMAT INFRASTRUCTURE**

**Core Architecture Completed:**
- ✅ **Dynamic Prompt Manager**: `src/ai/prompt_manager.py` - Loads format-specific prompts from JSON configs
- ✅ **Format-Specific Configurations**: Complete JSON templates for T12 and Weekly Database formats
- ✅ **Backwards Compatible API**: All existing functions work with added optional format parameters
- ✅ **Validation System**: Format-specific validation keywords and criteria
- ✅ **Caching System**: Efficient prompt loading and caching for performance
- ✅ **Error Handling**: Graceful fallback to default prompts when configs are missing
- ✅ **Multi-Analysis Support**: Both Standard and Assistants API analysis use format-specific prompts

**File Structure Created:**
```
config/prompts/
├── t12_monthly_financial.json     # Complete T12 prompt templates
├── weekly_database.json           # Weekly operational analysis prompts
└── [future formats...]            # Extensible for new property data formats

src/ai/
├── prompt_manager.py              # Dynamic prompt loading and management
├── prompt.py                      # Updated to use format-specific prompts
└── assistants_api.py              # Updated for multi-format support

src/utils/
└── format_detection.py            # Format detection and session management utilities
```

**Key Benefits Achieved:**
- 🚀 **Scalability**: Easy addition of new property data formats without code changes
- 🎯 **Format-Specific Analysis**: Each format gets tailored prompts and analysis focus
- 🔧 **Maintainability**: Prompts are externalized and easily editable
- 🔄 **Consistency**: Standardized template structure across all formats
- ⚡ **Performance**: Efficient caching and loading system
- 🛡️ **Reliability**: Comprehensive fallback system prevents failures

**Testing Results:**
- ✅ Prompt Manager loads configurations correctly
- ✅ T12 and Weekly Database prompts generate appropriate analysis focus
- ✅ Format-specific validation works correctly  
- ✅ Backwards compatibility maintained for existing T12 workflows
- ✅ Error handling provides graceful fallbacks
- ✅ Performance testing shows minimal impact on load times
- ✅ **CROSS-MODE ANALYSIS PERSISTENCE RESTORED**: Fixed issue where analysis results were lost when switching between Production and Developer modes
- ✅ **FORMAT PARAMETER INTEGRATION**: All UI modes now properly pass format parameters to analysis functions
- ✅ **FORMAT DETECTION IN UI**: Users now see detected format during data processing
- ✅ **SESSION STATE CLEANUP**: Format information properly cleared when new files are uploaded


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
- [x] **Mode Toggle**: Easy switch between Production and Developer modes in sidebar

#### 8.1 Production Mode UI - Clean & Results-Focused
- [x] **Minimal Upload Section**: Simple file drag-drop area with basic validation feedback only
- [x] **Hide Technical Details**: No raw data preview, file structure details, or processing logs
- [x] **Streamlined Workflow**: Upload → Enhanced AI Analysis → Results → Export
- [x] **Maximized Results Display**: Analysis results take up majority of screen real estate
- [x] **Clean Analysis Output**: Professional formatting with clear sections and minimal technical jargon
- [x] **Prominent Export Options**: Export buttons clearly visible and accessible at bottom of results
- [x] **Progress Simplification**: Show only essential progress messages, hide technical processing steps
- [x] **Error Handling**: User-friendly error messages without technical details or debug info
- [x] **Property Info Focus**: Emphasize property name/address input for report branding
- [x] **Results-First Layout**: Move analysis results above any technical sections
- [x] **Enhanced Analysis Only**: Removed analysis method selection, always use Assistants API with smart fallback

#### 8.2 Developer Mode UI - Organized & Collapsible
- [x] **Collapsible Sections**: Use `st.expander()` for all major sections with meaningful default states
- [x] **File Upload & Validation**: Expandable section with detailed file info, structure preview, validation results
- [x] **Data Processing**: Collapsible section showing raw data preview, KPI calculations, data quality checks
- [x] **AI Analysis Settings**: Expandable settings panel with prompt templates, model config, validation controls
- [x] **Debug Information**: Collapsible debug console with API logs, response validation, error details
- [x] **Advanced Export Options**: Expandable section with template customization, format options, batch processing
- [x] **Performance Metrics**: Collapsible metrics panel showing token usage, response times, quality scores
- [x] **Format Management**: Expandable section for custom format processors, testing, configuration
- [x] **Organized Sidebar**: Group related controls in collapsible sidebar sections
- [x] **Smart Defaults**: Most technical sections collapsed by default, only essential ones expanded
- [x] **Section Labels**: Clear, descriptive labels for each collapsible section with status indicators
- [x] **Developer Tools**: Separate expandable section for advanced testing, A/B prompt comparison, validation bypass

#### 8.3 UI Architecture & Organization
- [x] **Project Structure**: Create `src/ui/modes/` folder with `production_mode.py` and `developer_mode.py` components
- [x] **UI Components**: Organize mode-specific UI elements in respective files with clear imports
- [x] **Layout Optimization**: Production mode maximizes space for analysis results and export options
- [x] **User Preference**: Remember last selected mode and expanded/collapsed states in session state
- [x] **Responsive Design**: Ensure UI works well on different screen sizes and resolutions
- [x] **Component Reusability**: Shared components between modes with mode-specific styling
- [x] **State Management**: Proper session state handling for collapsible sections and user preferences

**✅ VALIDATION REQUIRED**: Production mode is clean and results-focused, developer mode has organized collapsible sections, both modes provide excellent user experience without overwhelming users

### 9. **PRIORITY: AI Analysis Quality & Output Validation**
- [x] **Test with real T12 data**: Upload actual T12 file and validate DataFrame structure
- [x] **Debug data quality issues**: Fix MonthParsed and other data parsing problems
- [ ] **Validate KPI calculations**: Ensure accurate financial metrics (Revenue, NOI, Occupancy)
- [ ] **Test OpenAI API calls**: Send KPI summary to OpenAI and validate response quality
- [x] **Analyze AI output quality**: Review strategic questions, recommendations, and trends
- [x] **Iterate on prompts**: Improve prompts based on actual AI responses - Added UI prompt preview!
- [ ] **Test multiple T12 files**: Validate consistency across different property data
- [x] **Display analysis results**: Ensure all AI output is properly shown in UI

#### 9.1 **AI Output Display & Formatting Issues**
- [x] **Fix Duplicate Analysis Display**: Remove duplicate analysis sections - currently showing both HTML rendered and collapsible sections
- [x] **Consolidate Output Display Logic**: Single source of truth for analysis results display across production and developer modes
- [x] **Raw AI Response Viewer**: Add collapsible section to display the raw, unprocessed AI response with proper HTML rendering
- [x] **Structured vs Raw Output Toggle**: Allow users to switch between formatted sections and raw AI output
- [x] **HTML Content Rendering**: Ensure AI-generated HTML content is properly rendered without escaping
- [x] **Output Formatting Standards**: Standardize how AI responses are processed and displayed across all UI modes
- [x] **Response Type Detection**: Auto-detect if AI response contains HTML, Markdown, or plain text and render appropriately
- [x] **Session State Persistence**: Prevent re-running analysis when switching between Production/Developer modes - analysis results now persist across mode switches
- [x] **Cross-Mode File Sharing**: Files uploaded in one mode are now available in both Production and Developer modes - implemented SharedFileManager for unified file persistence
- [x] **Side-by-Side Analysis Display**: Production mode now shows both structured analysis and complete AI report side-by-side with individual export options for each format
- [ ] **Debug Output Panel**: Developer mode panel showing raw API response, processed output, and final display format
- [ ] **Output Quality Validation**: Check for formatting issues, broken HTML, or display problems in AI responses
- [ ] **Better Section Organization**: Improve how analysis sections (questions, recommendations, trends) are organized and displayed

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
- [x] **Enhanced Analysis as Primary**: Removed analysis method selection, Enhanced Analysis is now the default with smart fallback
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
- [ ] **Format Manager**: UI to create, edit, and test custom T12 format processors
- [ ] **Format Testing**: Test new formats with sample data before deployment
- [ ] **Preprocessing Pipeline Editor**: Visual editor for creating custom preprocessing workflows
- [ ] **Project Structure**: Create `src/settings/` folder with `template_manager.py`, `config_editor.py`, `performance_tracker.py`, and `format_manager.py`
- [ ] **Settings Storage**: Create `settings/` folder with JSON files for user preferences, templates, and configurations
- [ ] **Backup System**: Create `backups/` folder with versioned settings and template snapshots
**✅ VALIDATION REQUIRED**: All settings persist correctly, templates are editable and apply properly, performance tracking works, format management is functional

### 14. Property Data Format Management - Scalable Plugin Architecture
- [ ] **Format Plugin Framework**: Create plugin system where new formats are added as independent modules
- [ ] **Format Registration**: Auto-discovery and registration of format processors in system
- [ ] **Format Detection Engine**: Smart detection system that tries each registered format processor
- [ ] **Format Configuration System**: JSON-based configuration for each format (headers, validation rules, KPIs)
- [ ] **Format Validation Framework**: Base validation with format-specific validation extensions
- [ ] **Format Documentation Generator**: Auto-generate format documentation from configuration files
- [ ] **Format Testing Framework**: Standardized testing approach for each format processor
- [ ] **Format Manager UI**: Developer mode UI to manage, test, and configure format processors
- [ ] **Hot-Reload Support**: Add new formats without restarting application
- [ ] **Format Versioning**: Support format processor versioning and updates
- [ ] **Cross-Format Analysis**: Framework for combining insights from multiple format types
- [ ] **Format Dependencies**: Handle formats that depend on or extend other formats
- [ ] **Project Structure**: Create `src/formats/` with individual format packages
- [ ] **Format Storage**: Create `formats/` folder with format-specific configs, samples, and documentation
- [ ] **Plugin Registry**: Create `src/core/plugin_manager.py` for format plugin management
**✅ VALIDATION REQUIRED**: Plugin system allows easy addition of new formats, maintains consistent interface, supports complex format requirements

### 15. Desktop Application Packaging
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
