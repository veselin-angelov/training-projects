import tkinter as tk
from helpers import create_connection, fetchall
from statistics import get_stats

connection = create_connection(
    "ekatte", "postgres", "admin", "127.0.0.1", "5432"
)


def show_data():
    word = entry.get()

    if word:
        q = f"SELECT * FROM settlements WHERE name LIKE '%{word}%';"
        responses = fetchall(connection, q)

        answer.config(state=tk.NORMAL)
        answer.delete('1.0', tk.END)

        for response in responses:
            result = {
                'ekatte': response[1],
                'settlement': response[2] + response[3],
                'muncipality': response[4],
            }

            answer.insert(tk.END, f"{result}\n")

        answer.config(state=tk.DISABLED)


if __name__ == '__main__':
    window = tk.Tk()
    window.geometry('800x600')

    label = tk.Label(text="Input keyword")
    entry = tk.Entry()
    button = tk.Button(
        text="Search!",
        width=25,
        height=2,
        command=show_data
    )
    answer = tk.Text()
    answer.config(state=tk.DISABLED)
    stats_label = tk.Label(text=get_stats(connection))

    label.pack()
    entry.pack()
    button.pack()
    answer.pack()
    stats_label.pack()

    window.mainloop()
