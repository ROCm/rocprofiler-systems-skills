---
name: unit-tests
description: Plan and write C++ unit tests using GTest and GMock - creates test plan and implements tests one by one with user approval
---

# Unit Testing Skill

Use this skill when writing unit tests for C++ code using Google Test (GTest) and Google Mock (GMock).

<IMPORTANT>
**When to trigger this skill:**
After completing a feature, refactoring, or bugfix, ASK the user:

> "Implementacija je završena. Da li želiš da dodam unit testove?
> - Koje komponente/funkcije treba testirati?
> - Da li ima specifičnih edge case-ova koje treba pokriti?"

If user agrees, follow the planning process below.

**Test-by-test approval:**
Write ONE test at a time, then STOP and wait for user approval before writing the next test.
</IMPORTANT>

## Phase 1: Analyze Testable Code

Before writing tests, identify:

1. **Public API** - Functions/methods that should be tested
2. **Dependencies** - What needs to be mocked
3. **Edge cases** - Boundary conditions, error states, empty inputs
4. **Invariants** - Conditions that must always hold

## Phase 2: Create Test Plan

Save to `planning/tests-<component>.md`:

```markdown
# Test Plan: <Component Name>

## Scope
<What is being tested>

## Test Cases

### <Function/Class 1>
- [ ] Test: <test name> - <what it verifies>
- [ ] Test: <test name> - <what it verifies>

#### Edge Cases
- [ ] <edge case description>
- [ ] <edge case description>

### <Function/Class 2>
...

## Mocks Required
- [ ] `mock_<name>` - mocks `<interface>` for <purpose>
- [ ] `mock_<name>` - mocks `<interface>` for <purpose>

## Test Fixtures
- [ ] `<fixture_name>` - shared setup for <test group>
```

## Phase 3: Implement Tests (One by One)

<IMPORTANT>
**CRITICAL: Test-by-test workflow**

1. Write ONE test
2. Show it to the user
3. Say: "Evo testa za <description>. Da li je OK? Mogu da nastavim sa sledećim testom?"
4. WAIT for user approval
5. Only after approval, proceed to next test
6. Mark completed test in plan file

DO NOT write multiple tests at once!
</IMPORTANT>

## GTest/GMock Patterns

### Basic Test Structure

```cpp
#include <gtest/gtest.h>
#include <gmock/gmock.h>

// Test case naming: TestSuiteName_TestName
TEST(calculator_test, add_returns_sum_of_two_numbers)
{
    calculator calc;
    EXPECT_EQ(calc.add(2, 3), 5);
}
```

### Test Fixture

```cpp
class parser_test : public ::testing::Test
{
protected:
    void SetUp() override
    {
        m_parser = std::make_unique<parser>();
    }

    void TearDown() override
    {
        m_parser.reset();
    }

    std::unique_ptr<parser> m_parser;
};

TEST_F(parser_test, parse_empty_input_returns_nullopt)
{
    EXPECT_EQ(m_parser->parse(""), std::nullopt);
}
```

### Creating Mocks

```cpp
// Interface to mock
class i_database
{
public:
    virtual ~i_database() = default;
    virtual bool save(const record& r) = 0;
    virtual std::optional<record> find(int id) = 0;
};

// Mock class
class mock_database : public i_database
{
public:
    MOCK_METHOD(bool, save, (const record& r), (override));
    MOCK_METHOD(std::optional<record>, find, (int id), (override));
};
```

### Using Mocks

```cpp
using ::testing::Return;
using ::testing::_;
using ::testing::NiceMock;
using ::testing::StrictMock;

TEST_F(service_test, process_saves_to_database)
{
    NiceMock<mock_database> mock_db;
    service svc(mock_db);

    EXPECT_CALL(mock_db, save(_))
        .WillOnce(Return(true));

    EXPECT_TRUE(svc.process(some_data));
}
```

### Common Matchers

```cpp
using namespace ::testing;

// Value matchers
EXPECT_THAT(value, Eq(expected));
EXPECT_THAT(value, Ne(unexpected));
EXPECT_THAT(value, Lt(max));
EXPECT_THAT(value, Gt(min));
EXPECT_THAT(value, Le(max));
EXPECT_THAT(value, Ge(min));

// String matchers
EXPECT_THAT(str, StartsWith("prefix"));
EXPECT_THAT(str, EndsWith("suffix"));
EXPECT_THAT(str, HasSubstr("middle"));
EXPECT_THAT(str, MatchesRegex("pattern"));

// Container matchers
EXPECT_THAT(vec, IsEmpty());
EXPECT_THAT(vec, SizeIs(5));
EXPECT_THAT(vec, Contains(element));
EXPECT_THAT(vec, ElementsAre(1, 2, 3));
EXPECT_THAT(vec, UnorderedElementsAre(3, 1, 2));
EXPECT_THAT(vec, Each(Gt(0)));

// Pointer matchers
EXPECT_THAT(ptr, IsNull());
EXPECT_THAT(ptr, NotNull());
EXPECT_THAT(ptr, Pointee(Eq(value)));

// Optional matchers (custom or use value)
EXPECT_TRUE(opt.has_value());
EXPECT_EQ(opt.value(), expected);
```

### Testing Exceptions

```cpp
TEST(parser_test, parse_invalid_throws_exception)
{
    parser p;
    EXPECT_THROW(p.parse("invalid"), parse_error);
}

TEST(parser_test, parse_invalid_throws_with_message)
{
    parser p;
    EXPECT_THROW(
        {
            try {
                p.parse("invalid");
            } catch (const parse_error& e) {
                EXPECT_THAT(e.what(), HasSubstr("invalid"));
                throw;
            }
        },
        parse_error
    );
}
```

### Parameterized Tests

```cpp
class add_test : public ::testing::TestWithParam<std::tuple<int, int, int>>
{
};

TEST_P(add_test, returns_correct_sum)
{
    auto [a, b, expected] = GetParam();
    calculator calc;
    EXPECT_EQ(calc.add(a, b), expected);
}

INSTANTIATE_TEST_SUITE_P(
    calculator_tests,
    add_test,
    ::testing::Values(
        std::make_tuple(0, 0, 0),
        std::make_tuple(1, 1, 2),
        std::make_tuple(-1, 1, 0),
        std::make_tuple(INT_MAX, 0, INT_MAX)
    )
);
```

## Edge Cases Checklist

Always consider testing:

### Boundary Values
- [ ] Zero / empty
- [ ] One element / single character
- [ ] Maximum values (INT_MAX, SIZE_MAX)
- [ ] Minimum values (INT_MIN, 0 for unsigned)
- [ ] Just below/above boundaries

### Error Conditions
- [ ] Null pointers (if applicable)
- [ ] Empty containers
- [ ] Invalid input
- [ ] Resource exhaustion
- [ ] Timeout scenarios

### State Transitions
- [ ] Initial state
- [ ] After single operation
- [ ] After multiple operations
- [ ] After error recovery

## Test Naming Convention

Use descriptive names that explain:
1. **What** is being tested
2. **Under what conditions**
3. **Expected result**

```cpp
// Pattern: <unit>_<scenario>_<expected_result>
TEST(parser_test, parse_empty_string_returns_nullopt)
TEST(parser_test, parse_valid_json_returns_document)
TEST(parser_test, parse_invalid_json_throws_parse_error)
TEST(calculator_test, divide_by_zero_throws_domain_error)
```

## Test File Organization

```
tests/
├── CMakeLists.txt
├── unit/
│   ├── test_calculator.cpp
│   ├── test_parser.cpp
│   └── mocks/
│       ├── mock_database.hpp
│       └── mock_network.hpp
└── integration/
    └── test_system.cpp
```

### CMakeLists.txt for Tests

```cmake
enable_testing()

find_package(GTest REQUIRED)

add_executable(unit_tests
    unit/test_calculator.cpp
    unit/test_parser.cpp
)

target_link_libraries(unit_tests
    PRIVATE
        GTest::gtest_main
        GTest::gmock
        mylib  # Library being tested
)

include(GoogleTest)
gtest_discover_tests(unit_tests)
```

## References

- [GoogleTest Primer](https://google.github.io/googletest/primer.html)
- [GoogleTest Advanced](https://google.github.io/googletest/advanced.html)
- [GoogleMock for Dummies](https://google.github.io/googletest/gmock_for_dummies.html)
- [Matchers Reference](https://google.github.io/googletest/reference/matchers.html)
