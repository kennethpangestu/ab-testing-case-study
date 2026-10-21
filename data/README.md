# Data

`cookie_cats.csv`: results of an A/B test in the mobile puzzle game *Cookie Cats* by Tactile Entertainment. Players were randomly assigned at install to have the first gate at level 30 (control) or level 40 (treatment).

The dataset was originally released through a DataCamp project and is widely mirrored for teaching. This copy was taken from the public repository [robguilarr/ab_testing_cookie_cats](https://github.com/robguilarr/ab_testing_cookie_cats).

| Column | Description |
|---|---|
| `userid` | Unique player ID |
| `version` | `gate_30` (control) or `gate_40` (treatment) |
| `sum_gamerounds` | Game rounds played in the first 14 days after install |
| `retention_1` | Whether the player came back and played 1 day after install |
| `retention_7` | Whether the player came back and played 7 days after install |

90,189 rows, no missing values, no duplicate `userid`s.
