import pandas as pd
from datetime import datetime
import os


def process_data(folder_path, n):
    # 1) Combine data from closePosition CSVs
    combined_data = pd.DataFrame(columns=['Key', 'ExitTime', 'Symbol', 'EntryPrice', 'Quantity', 'Pnl', 'Date'])
    for filename in os.listdir(folder_path):
        if "closePosition" in filename and filename.endswith(".csv"):
            data = pd.read_csv(os.path.join(folder_path, filename))
            data["Date"] = pd.to_datetime(data["ExitTime"]).dt.date
            combined_data = pd.concat(
                [combined_data if not combined_data.empty else None, data if not data.empty else None],
                ignore_index=True)
    combined_data.to_csv("combined_closePosition.csv", index=False)

    # 2) Calculate statistics and save to txt file
    stats = {
        "Total trades": len(combined_data),
        "Unique days": combined_data["Date"].nunique(),
        "Average trades": len(combined_data) / combined_data["Date"].nunique(),
        "Total Pnl": combined_data["Pnl"].sum(),
        "Profit Trades": (combined_data["Pnl"] > 0).sum(),
        "Loss Trades": (combined_data["Pnl"] <= 0).sum()
    }

    with open("combined_stats.txt", "w") as f:
        for key, value in stats.items():
            f.write(f"{key}: {value}\n")

    # 3) Identify winning/losing streaks
    combined_data.sort_values(by="ExitTime", inplace=True)
    streak_type = None
    current_streak = []
    winning_streaks = []
    losing_streaks = []
    for i in range(len(combined_data)):
        row = combined_data.iloc[i]
        if streak_type is None:
            streak_type = "winning" if row["Pnl"] > 0 else "losing"
        elif (streak_type == "winning" and row["Pnl"] <= 0) or (streak_type == "losing" and row["Pnl"] > 0):
            # End of streak
            if streak_type == "winning":
                winning_streaks.append(current_streak)
            else:
                losing_streaks.append(current_streak)
            streak_type = None
            current_streak = []
        current_streak.append(row)
    # Add the last streak if it exists
    if current_streak:
        if streak_type == "winning":
            winning_streaks.append(current_streak)
        else:
            losing_streaks.append(current_streak)

    # Sort streaks by total Pnl and select top n
    winning_streaks.sort(key=lambda x: sum(row["Pnl"] for row in x), reverse=True)
    losing_streaks.sort(key=lambda x: sum(row["Pnl"] for row in x))
    top_n_winning = winning_streaks[:n]
    top_n_losing = losing_streaks[:n]

    # Save streaks to txt file
    with open("combined_winning_losing.txt", "w") as f:
        f.write("Top {} winning streaks\n".format(n))
        for i, streak in enumerate(top_n_winning):
            start_date = streak[0]["Date"].strftime("%Y-%m-%d")
            end_date = streak[-1]["Date"].strftime("%Y-%m-%d")
            total_pnl = sum(row["Pnl"] for row in streak)
            f.write(
                f"{i + 1}) {len(streak)} trades        {start_date}     to      {end_date}           profit: {total_pnl}\n")

        f.write("\nTop {} losing streaks\n".format(n))
        for i, streak in enumerate(top_n_losing):
            start_date = streak[0]["Date"].strftime("%Y-%m-%d")
            end_date = streak[-1]["Date"].strftime("%Y-%m-%d")
            total_pnl = sum(row["Pnl"] for row in streak)
            f.write(
                f"{i + 1}) {len(streak)} trades        {start_date}     to      {end_date}           loss: {total_pnl}\n")


data_file_path = input("Enter the file path: ")
no_of_entries = input("Enter the no of entries: ")

process_data(data_file_path, int(no_of_entries))
