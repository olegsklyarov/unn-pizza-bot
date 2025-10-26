# Lecture Plan: QA Tools and Testing for Telegram Bot Development
## Duration: 90 minutes | Format: Blackboard + Live Coding

---

## **Part 1: Introduction & Code Quality Tools (25 minutes)**

### **Opening: The Problem (5 minutes)**
- **Blackboard**: Draw diagram of messy, untested code vs. clean, tested code
- **Real-world impact**: Bugs in production, maintenance nightmares, team collaboration issues
- **Today's goal**: Transform a working bot into a maintainable, testable system

### **Code Quality Tools Overview (10 minutes)**
- **Blackboard**: Draw the QA pipeline: Code → Format → Lint → Test → Deploy
- **Live Demo**: Show current bot code structure
  ```bash
  # Show current project structure
  tree bot/
  cat requirements.txt
  ```

### **Black: Code Formatting (10 minutes)**
- **Blackboard**: Explain why consistent formatting matters
- **Live Coding**:
  ```bash
  # Install and configure Black
  pip install black

  # Format code
  black bot/

  # Show before/after
  # Configure in pyproject.toml
  ```
- **Student Exercise**: Format their own code snippets

---

## **Part 2: Linting with Ruff (20 minutes)**

### **Ruff Introduction (5 minutes)**
- **Blackboard**: Draw linting process - static analysis without running code
- **Why Ruff**: Fast, comprehensive, replaces multiple tools

### **Live Coding Session (15 minutes)**
```bash
# Install Ruff
pip install ruff

# Run checks
ruff check bot/

# Auto-fix issues
ruff check --fix bot/

# Show configuration options
```

### **Student Practice (5 minutes)**
- Students run Ruff on their code
- Discuss common issues found
- **Blackboard**: Write down most common linting rules

---

## **Part 3: Code Architecture Refactoring (25 minutes)**

### **The Problem: Tight Coupling (5 minutes)**
- **Blackboard**: Draw current architecture with direct dependencies
- Show current handlers directly importing SQLite and Telegram API
- **Problem**: Hard to test, hard to change, violates SOLID principles

### **Dependency Inversion Pattern (10 minutes)**
- **Blackboard**: Draw the new architecture with interfaces
- **Key concepts**:
  - Abstract base classes (ABC)
  - Interface segregation
  - Dependency injection
- **Live Demo**: Show current `Storage` and `Messenger` interfaces

### **Live Refactoring Session (10 minutes)**
- **Show current handler**:
  ```python
  # Before: Direct imports
  from bot.infrastructure.storage_sqlite import StorageSQLite
  from bot.infrastructure.messenger_telegram import MessengerTelegram
  ```
- **Refactor to**:
  ```python
  # After: Interface-based
  from bot.domain.storage import Storage
  from bot.domain.messenger import Messenger
  ```
- **Blackboard**: Draw the new layered architecture

---

## **Part 4: Testing with Pytest (20 minutes)**

### **Testing Philosophy (5 minutes)**
- **Blackboard**: Draw testing pyramid (Unit → Integration → E2E)
- **Why unit tests**: Fast, isolated, reliable feedback
- **Mocking**: Replace external dependencies

### **Live Coding: First Test (15 minutes)**
- **Show the custom Mock class**:
  ```python
  # tests/mock.py
  class Mock:
      def __init__(self, dictionary: dict) -> None:
          for k, v in dictionary.items():
              setattr(self, k, v)
  ```

- **Write UpdateDatabaseLogger test**:
  ```python
  def test_update_database_logger_execution():
      # 1. Create test data
      test_update = {...}

      # 2. Create mocks
      mock_storage = Mock({"persist_update": persist_update})

      # 3. Test through dispatcher
      dispatcher.dispatch(test_update)

      # 4. Assertions
      assert persist_update_called
  ```

### **Student Exercise (5 minutes)**
- Students write a simple test for `EnsureUserExists` handler
- Pair programming: help debug issues

---

## **Part 5: Advanced Testing & CI/CD (15 minutes)**

### **Complex Handler Testing (10 minutes)**
- **Live Coding**: Test `MessageStart` handler
- **Show multiple assertions**:
  - Storage method calls
  - Messenger method calls
  - Return status verification
- **Blackboard**: Draw test flow diagram

### **GitHub Actions Integration (5 minutes)**
- **Show CI workflow**:
  ```yaml
  - name: Run Black code style check
  - name: Run Ruff linting check
  - name: Run pytest tests
  ```
- **Live Demo**: Push changes and show CI running
- **Benefits**: Automated quality gates, team confidence

---

## **Part 6: Wrap-up & Best Practices (5 minutes)**

### **Key Takeaways (3 minutes)**
- **Blackboard**: Draw the complete QA pipeline
- **Code Quality**: Format → Lint → Test → Deploy
- **Architecture**: Interfaces enable testing
- **Testing**: Mock external dependencies

### **Next Steps (2 minutes)**
- **Homework**: Add tests for remaining handlers
- **Resources**:
  - Black documentation
  - Ruff rules reference
  - Pytest best practices
- **Questions & Discussion**

---

## **Materials Needed**

### **Technical Setup**
- Projector + laptop with IDE
- Blackboard/whiteboard
- Student laptops with Python environment
- GitHub repository access

### **Code Examples**
- Current bot code (before refactoring)
- Refactored code with interfaces
- Complete test suite
- GitHub Actions workflow

### **Handouts**
- Quick reference: Black commands
- Ruff rules cheat sheet
- Pytest assertion methods
- Testing best practices checklist

---

## **Timing Breakdown**
- **Introduction & Tools**: 25 min
- **Ruff Linting**: 20 min
- **Architecture Refactoring**: 25 min
- **Pytest Testing**: 20 min
- **CI/CD & Wrap-up**: 15 min
- **Total**: 90 minutes

---

## **Learning Objectives**

By the end of this lecture, students will be able to:
1. **Format code** using Black consistently
2. **Identify and fix** code quality issues with Ruff
3. **Refactor code** to use dependency inversion
4. **Write unit tests** with pytest and mocking
5. **Set up CI/CD** with GitHub Actions
6. **Apply QA practices** to their own projects

---

## **Assessment**
- **During**: Live coding participation, Q&A
- **After**: Homework assignment to add tests to their own bot handlers
- **Follow-up**: Code review session next week
