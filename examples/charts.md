+++
title = "Charts Showcase"
palette = "vivid"
+++

# Charts Showcase
A demo of all chart types and options available in md2.

---

## Bar Chart

:::chart bar --labels
| Product  | Revenue |
|----------|---------|
| Alpha    | 120     |
| Beta     | 85      |
| Gamma    | 200     |
| Delta    | 150     |
:::

---

## Column Chart (Multi-Dataset)

:::chart column --labels --legend
| Quarter | Sales | Expenses |
|---------|-------|----------|
| Q1      | 100   | 80       |
| Q2      | 150   | 90       |
| Q3      | 130   | 110      |
| Q4      | 200   | 120      |
:::

---

## Stacked Bar

:::chart bar --labels --legend --stacked
| Team        | Frontend | Backend | DevOps |
|-------------|----------|---------|--------|
| Alpha       | 30       | 50      | 20     |
| Beta        | 40       | 35      | 25     |
| Gamma       | 25       | 60      | 15     |
:::

---

## Line Chart

:::chart line --labels --show-data
| Month | Users |
|-------|-------|
| Jan   | 100   |
| Feb   | 180   |
| Mar   | 250   |
| Apr   | 310   |
| May   | 420   |
| Jun   | 500   |
:::

---

## Area Chart

:::chart area --labels
| Hour  | CPU Load |
|-------|----------|
| 08:00 | 20       |
| 10:00 | 55       |
| 12:00 | 80       |
| 14:00 | 70       |
| 16:00 | 90       |
| 18:00 | 40       |
:::

---

## Chart with Title

:::chart column --labels --title "Quarterly Revenue ($K)"
| Quarter | Revenue |
|---------|---------|
| Q1      | 340     |
| Q2      | 520     |
| Q3      | 480     |
| Q4      | 710     |
:::
