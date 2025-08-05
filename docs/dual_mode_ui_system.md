# Dual-Mode UI System Documentation

## Overview

The T12 Property Analysis Tool now features a sophisticated dual-mode UI system that provides two distinct user experiences:

- **🏭 Production Mode**: Clean, streamlined interface for end-users
- **🛠️ Developer Mode**: Advanced interface with debugging tools and detailed controls

## Quick Start

### Switching Modes

1. Look for the **Interface Mode** selector in the sidebar (top section)
2. Choose between "🏭 Production" or "🛠️ Developer"
3. The interface will automatically refresh to show the selected mode

### Mode Comparison

| Feature | Production Mode | Developer Mode |
|---------|----------------|----------------|
| **Layout** | 2-column (1:2.5 ratio) | 3-column (1:2:1 ratio) |
| **Sidebar** | Essential settings only | Full configuration options |
| **File Processing** | Basic validation | Detailed validation + raw data |
| **KPI Analysis** | Summary view | Summary + detailed breakdown |
| **AI Analysis** | Standard processing | Advanced settings + debugging |
| **Debug Tools** | Hidden | Debug console + logs |
| **Raw Data Access** | Limited | Full inspection tools |
| **Export Options** | Basic formats | All formats + metadata |

## Production Mode Features

### 🎯 **Optimized for End-Users**
- Clean, minimal interface
- Focus on core workflow
- Essential settings only
- Streamlined process flow

### 📊 **Key Sections**
1. **File Upload**: Simple drag-and-drop interface
2. **Data Processing**: Automated with progress tracking
3. **KPI Summary**: Key metrics at a glance
4. **AI Analysis**: One-click analysis with results
5. **Export**: Quick download options

### ⚡ **Benefits**
- Reduced cognitive load
- Faster task completion
- Fewer configuration errors
- Better focus on results

## Developer Mode Features

### 🛠️ **Advanced Tools**
- Comprehensive debugging console
- Raw data inspection
- Advanced API settings
- Detailed error logs

### 🔧 **Debug Console**
- Real-time operation logs
- Error tracking and analysis
- Performance monitoring
- Session state inspection

### 📈 **Enhanced Analytics**
- Detailed KPI breakdowns
- Format processor insights
- Calculation transparency
- Performance metrics

### ⚙️ **Advanced Settings**
- Custom API parameters
- Temperature control
- Token limits
- Model selection

## Technical Architecture

### Base Classes

```python
# Abstract base for all UI modes
class BaseUIMode:
    def render_sidebar(self, ...)
    def render_main_content(self, ...)
    def get_layout_config(self)
    def should_show_feature(self, feature_name)
```

### Mode Manager

```python
# Central mode management
class UIModeManager:
    def register_mode(self, mode)
    def set_current_mode(self, mode_name)
    def render_current_mode(self, uploaded_file)
    def handle_mode_transition(self, from_mode, to_mode)
```

### Integration Points

The dual-mode system integrates with:
- **Scalable Format System** (Section 3)
- **Scalable KPI System** (Section 4)
- **Legacy UI Components** (backward compatibility)
- **Progress Tracking System**
- **Export System**

## Usage Examples

### Basic Mode Switching
```python
from src.ui.modes import render_current_mode, get_current_mode

# Render current mode
render_current_mode(uploaded_file)

# Check current mode
current_mode = get_current_mode()
```

### Feature Visibility Control
```python
from src.ui.modes import should_show_feature

# Show advanced features only in developer mode
if should_show_feature('debug_console'):
    st.expander("Debug Console")
```

### Layout Configuration
```python
from src.ui.modes import get_layout_config

config = get_layout_config()
columns = st.columns(config['column_ratios'])
```

## Customization

### Adding New Modes

1. **Create Mode Class**:
```python
class CustomMode(BaseUIMode):
    mode_name = "custom"
    mode_description = "Custom interface mode"
    
    def render_sidebar(self, ...):
        # Custom sidebar implementation
    
    def render_main_content(self, ...):
        # Custom main content implementation
```

2. **Register Mode**:
```python
from src.ui.modes import ui_mode_manager
ui_mode_manager.register_mode(CustomMode())
```

### Feature Flags

Modes support feature flags for granular control:

```python
# In mode implementation
def should_show_feature(self, feature_name: str) -> bool:
    feature_map = {
        'debug_console': self.mode_name == 'developer',
        'raw_data_access': self.mode_name in ['developer', 'custom'],
        'advanced_settings': self.mode_name != 'production'
    }
    return feature_map.get(feature_name, True)
```

## Best Practices

### For End-Users
1. **Start with Production Mode** for routine analysis
2. **Switch to Developer Mode** when troubleshooting
3. **Use Export Options** appropriate for your needs

### For Developers
1. **Test in both modes** when making changes
2. **Use feature flags** to control visibility
3. **Monitor debug console** for performance insights
4. **Document mode-specific features**

### For Administrators
1. **Set default mode** based on user type
2. **Monitor usage patterns** between modes
3. **Customize feature availability** per organization
4. **Train users** on mode selection

## Troubleshooting

### Common Issues

**Mode not switching:**
- Check session state initialization
- Verify mode registration
- Clear browser cache

**Features not showing:**
- Check feature flag implementation
- Verify mode-specific logic
- Review should_show_feature() method

**Performance issues:**
- Monitor debug console in Developer Mode
- Check session state size
- Optimize mode transition logic

### Debug Commands

```python
# Check registered modes
from src.ui.modes import ui_mode_manager
print(ui_mode_manager.get_available_modes())

# Reset all modes
ui_mode_manager.reset_all_modes()

# Get mode info
mode_info = ui_mode_manager.get_mode_info('developer')
```

## Future Enhancements

### Planned Features
- **Role-based mode selection**
- **Custom mode templates**
- **Usage analytics dashboard**
- **A/B testing framework**

### Extension Points
- **Plugin architecture** for third-party modes
- **Theme system** integration
- **Workflow templates** per mode
- **Integration APIs** for external tools

---

*This dual-mode system provides a scalable foundation for different user experiences while maintaining code reusability and extensibility.*
