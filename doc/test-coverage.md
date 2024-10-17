# How to Generate Coverage Reports

To generate your coverage reports using the configuration in your .coveragerc, follow these steps:

1. **Run Tests with Coverage:** Navigate to your project directory (where your .coveragerc file is located) and run your tests with coverage:
```bash
cd /path/to/airtable-sync
coverage run -m unittest discover -s test -v
```
This will execute all your unit tests and collect coverage data according to your .coveragerc settings.

2. **Generate Coverage Report:** You can generate a console report with the following command:
```bash
coverage report -m
```
This will display a report in your terminal, showing which lines of code were covered by tests and which were not, alongside a percentage of coverage.

3. **Generate HTML Report:** To create an HTML report, simply run:
```bash
coverage html
```
This will generate the HTML report in the directory specified in the [html] section of your .coveragerc file (i.e., .coverage/html).

4. **View the HTML Report:** Open the generated HTML report in your web browser:
```bash
open .coverage/html/index.html  # macOS
xdg-open .coverage/html/index.html  # Linux
start .coverage/html/index.html  # Windows
```