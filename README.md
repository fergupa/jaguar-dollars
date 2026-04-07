# Jaguar Dollars

A school reward system where teachers award "Jaguar Dollars" to students for good behavior, and students redeem them for prizes.

## Quick Start

```bash
cd jaguar-dollars
pip install -r requirements.txt
streamlit run app.py
```

The app auto-seeds demo data on first run. Open `http://localhost:8501` in your browser.

## Demo Credentials

### Teachers
| Username | Password | Name | Classroom |
|----------|----------|------|-----------|
| mrivera | jaguar123 | Mrs. Rivera | Room 204 - Science |
| mthompson | jaguar123 | Mr. Thompson | Room 112 - English |
| mchen | jaguar123 | Ms. Chen | Room 301 - Math |
| rcanada | jaguar123 | Rob Canada | Room 405 - Social Studies |

### Students
| Username | Password | Name | Classroom |
|----------|----------|------|-----------|
| jsmith | student | Jordan Smith | Science |
| agarcia | student | Alex Garcia | Science |
| mwilson | student | Maya Wilson | Science |
| dlee | student | David Lee | Science |
| sbrooks | student | Sofia Brooks | Science |
| tjohnson | student | Tyler Johnson | English |
| kpatel | student | Kira Patel | English |
| rmartin | student | Ryan Martin | English |
| enguyen | student | Emma Nguyen | English |
| jwilliams | student | Jake Williams | English |
| lrodriguez | student | Lily Rodriguez | Math |
| okim | student | Owen Kim | Math |
| cjones | student | Chloe Jones | Math |
| abrown | student | Aiden Brown | Math |
| zthomas | student | Zoe Thomas | Math |

## Features

### Teachers
- **Dashboard** - Overview stats and quick award form
- **Give Dollars** - Award to individual or multiple students
- **Manage Prizes** - Create, edit, activate/deactivate prizes
- **Nominations** - Review and approve/deny student nominations
- **Class Pools** - Manage classroom pool balances and redeem class prizes

### Students
- **My Jaguar Dollars** - Balance display with goal tracker
- **Prize Store** - Browse and redeem prizes
- **Nominate** - Nominate classmates for Jaguar Dollars
- **Class Pool** - Contribute to classroom pool for class prizes
- **History** - View all transaction history

## How It Works

1. Teachers have a bank of 500 Jaguar Dollars to distribute
2. Teachers award dollars to students for good behavior, homework, participation, etc.
3. Students accumulate dollars and can redeem them for prizes
4. Students can nominate classmates - teacher reviews and approves
5. Students can pool dollars by classroom for bigger class prizes

## Reset Data

Delete `jaguar_dollars.db` and restart the app to re-seed fresh demo data.
