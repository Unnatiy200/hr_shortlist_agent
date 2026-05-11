***# How to Use the HR Shortlist Agent***



***## First Time Setup (Do this once only)***



***1. Make sure Python is installed on your computer***

   ***- Download from: https://python.org***

   ***- During install: CHECK the box "Add Python to PATH"***



***2. Add your Groq API key to the .env file***

   ***- Open the .env file in Notepad***

   ***- Replace "your\_groq\_key\_here" with your actual key***

   ***- Get a free key from: https://console.groq.com***

   ***- Save and close***



***---***



***## Every Time You Use It***



***### Step 1 — Start the app***

***Double-click the START.bat file***

***The app will open in your browser automatically.***



***### Step 2 — Enter the Job Description***

***- Paste the job description into the text box***

***- Or use the pre-filled sample JD to test***



***### Step 3 — Add Candidates***

***You have 3 options:***

***- OPTION A: Upload PDF or DOCX resume files***

***- OPTION B: Check the box to use 5 sample candidates***

***- OPTION C: Manually type a LinkedIn profile***



***### Step 4 — Run the Agent***

***Click the big blue button:***

***"Run AI Scoring Agent"***

***Wait 30-60 seconds while it scores all candidates.***



***### Step 5 — View Results***

***- See all candidates ranked by score***

***- Click any candidate to see detailed breakdown***

***- Green = Hire, Yellow = Review, Red = No Hire***



***### Step 6 — Override a Score (Optional)***

***If you disagree with a score:***

***- Expand the candidate card***

***- Select the dimension to change***

***- Enter new score and reason***

***- Click Apply Override***

***- All changes are saved automatically***



***### Step 7 — Download Report***

***- Click "Generate HTML Report" for a visual report***

***- Click "Generate JSON Report" for data export***

***- Both download to your computer***



***---***



***## Understanding the Scores***



***| Score | Meaning |***

***|---|---|***

***| 7.5 - 10 | Recommended Hire |***

***| 5.0 - 7.4 | Needs Further Review |***

***| 0 - 4.9 | Not Suitable |***



***## Scoring Dimensions***



***| Dimension | Weight | What it measures |***

***|---|---|---|***

***| Skills Match | 30% | How many required skills the candidate has |***

***| Experience | 25% | How relevant their work history is |***

***| Education | 15% | Qualifications and certifications |***

***| Projects | 20% | Evidence of real work and portfolio |***

***| Communication | 10% | Clarity of their resume writing |***



***---***



***## Troubleshooting***



***\*\*App does not open:\*\****

***- Make sure you double-clicked START.bat***

***- Try opening browser manually: http://localhost:8501***



***\*\*Error: Module not found:\*\****

***- Run START.bat again — it will reinstall packages***



***\*\*Scoring takes too long:\*\****

***- Normal wait time is 30-60 seconds per 5 candidates***

***- Do not close the browser tab***



***\*\*Results look wrong:\*\****

***- Use the HR Override feature to correct any score***

***- All overrides are logged with your reason***



***---***



***## Need Help?***

***Contact the developer or raise a GitHub issue.***

