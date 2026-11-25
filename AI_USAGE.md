# AI Usage Reflection

## AI Tools Used

During the development of PennyWise, I used two AI tools: GitHub Copilot and ChatGPT.

- **GitHub Copilot in Visual Studio Code:** I used Copilot to generate code, modify project files, debug errors, and create automated tests.
- **ChatGPT:** I used ChatGPT to help translate my ideas into clear and detailed prompts, divide the project into development phases, and create a structured outline. This helped me manage the development process and track my progress more effectively.

## How AI Assisted

My initial idea was to build a personal finance application that would not only record expenses but also help users understand their spending habits and achieve their financial goals.

I used ChatGPT to organize my ideas into clear business requirements and break the project into smaller development phases. I then provided these requirements to GitHub Copilot for implementation.

Instead of developing the entire application at once, I worked through each phase, manually tested the functionality, identified areas for improvement, and provided additional instructions to AI when necessary. This approach made the development process easier to manage and allowed me to improve the application gradually.

## Where AI Was Helpful

AI was particularly helpful in turning my business ideas into functional application features. I could describe what I wanted the application to accomplish from a user's perspective, and AI helped implement the technical logic behind those requirements.

ChatGPT helped me communicate my ideas more clearly, while GitHub Copilot assisted with coding, debugging, and testing. This allowed me to focus more on the application's purpose, functionality, and user experience.

AI was also helpful when I encountered technical problems. It helped me understand error messages, identify possible causes, and find solutions without having to restart the entire project.

## Incorrect or Incomplete AI Output

Throughout development, I encountered several situations where AI-generated code was incorrect or did not fully meet my expectations.

**JSON storage issue:** During expense tracking development, an automated test revealed that the application loaded data from a temporary test file but saved changes to the default data file. Later, when I manually checked the expense records, I noticed a test transaction that I had not entered myself. The code was corrected to use the same file path for both loading and saving data. This helped me understand the importance of separating test data from actual user data.

**Regression testing issue:** When a new monthly spending report option was added, an existing automated test failed because it still used the previous menu number to exit the application. The test needed to be updated to match the new menu structure. This showed me how adding a new feature can affect previously working parts of an application.

**User experience issue:** One of the most important problems I personally discovered through manual testing occurred when the application had already passed 53 automated tests. Although the tests were successful, I had difficulty using the View Expenses and View Savings Goals features because the results were not clearly visible before the application returned to the main menu.

I reported this problem to AI and requested an investigation. The solution was to add a pause that allowed users to read the information before pressing Enter to return to the menu. Two additional integration tests were created to verify the new behavior.

These experiences taught me that AI-generated code should not be accepted without verification. Automated testing is important, but manual testing is also necessary to evaluate the application from a user's perspective and identify usability problems.

## How I Verified the Work

Throughout development, I manually ran the application in the Visual Studio Code terminal and tested its features using sample financial data.

I checked whether users could manage expenses, generate monthly spending reports, create and edit savings goals, add savings contributions, and receive financial recommendations. I also reviewed the displayed calculations, savings progress, and menu navigation to determine whether the results matched my expectations.

I ran automated tests using:

`python -m pytest -v`

After completing major development phases, I used Git to commit the changes and maintain a clear development history. The final code review reported 109 passing tests.

By combining automated testing with manual testing, I was able to evaluate both the technical functionality and the user experience of the application.

## Design Decisions I Made

Although AI assisted with the technical implementation, I actively developed the application's business requirements and made decisions about its functionality and user experience.

### Improving User Experience

As the application grew, I noticed that the main menu was becoming too long and difficult to navigate. I decided to group related functions into Manage Expenses and Manage Savings Goals submenus. This made the application more organized and easier to use without removing existing functionality.

I also noticed that the original expense and savings goal IDs were too long and inconvenient. I requested shorter, randomly generated expense reference IDs and numbered savings goal selections. I wanted savings goals to follow a numbered order that could represent the user's priorities.

Additionally, I requested more compact spending charts after noticing that the original bar charts were too long and wrapped onto another line in the terminal.

These improvements were based on my experience using the application rather than simply following the original AI-generated design.

### Developing the Monthly Savings Plan

I wanted the savings goal feature to provide more information than just the percentage of money already saved. I developed the idea of allowing users to enter their planned monthly savings contribution when creating a financial goal.

Using this information, the application calculates the estimated number of months required to achieve the goal. Users can also update their target amount and monthly contribution when their financial plans change.

This feature helps users understand whether their current savings plan matches their financial expectations.

### Connecting Financial Data and Business Logic

I wanted the AI Financial Coach to provide recommendations that were more meaningful and actionable.

Instead of only informing users that they were spending too much in a particular category, I requested a feature that calculates how reducing unnecessary expenses and redirecting that money toward a savings goal could improve their savings progress in the following month.

For example, if a user's shopping expenses exceed the suggested spending guideline, the financial coach recommends a potential spending reduction. It then uses the user's existing savings goal and planned monthly contribution to calculate the potential improvement in next month's savings progress.

This feature connects monthly spending data, financial recommendations, and savings goal information through rule-based business logic. It allows users to understand the potential impact of their spending decisions rather than simply receiving general financial advice.

My overall goal was to keep PennyWise simple, practical, and useful while making its features work together.

## What I Learned

Through this project, I gained a better understanding of how business requirements can be translated into functional software features.

I learned that developing an application involves more than writing code. It also requires understanding user needs, organizing requirements, connecting data with business logic, testing functionality, and continuously improving the user experience.

I also learned how to communicate with AI more effectively by providing clear requirements, dividing complex tasks into smaller steps, and evaluating the results before moving forward.

Another important lesson was understanding the difference between automated testing and manual testing. Even when all automated tests passed, I was still able to identify problems and opportunities for improvement by personally using the application.

Most importantly, I learned that AI is a useful development tool, but human involvement is still necessary to identify problems, make business decisions, and ensure that the final application meets its intended purpose.

## What I Would Do Differently Next Time

In future projects, I would spend more time planning the business requirements, user experience, and overall application structure before starting development.

During this project, several new ideas came from manually using the application. Although this helped improve PennyWise, defining more detailed requirements earlier could reduce unnecessary changes to existing code and tests.

I would also establish manual testing scenarios earlier in the development process instead of relying primarily on automated test results.

I would continue using AI for coding assistance, debugging, testing, and project planning while remaining actively involved in requirement development, manual testing, and evaluating whether the application meets users' needs.

Overall, AI made the development process more efficient, while my involvement in defining business requirements, developing ideas, verifying results, and improving the user experience helped shape the final application.