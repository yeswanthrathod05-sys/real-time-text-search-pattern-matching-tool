
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import time
import csv
from collections import Counter
from datetime import datetime
import os


# ============================================================
# REAL-TIME TEXT SEARCH & PATTERN MATCHING TOOL
# Advanced B.Tech Project
# Python Standard Library Only
# ============================================================


# ---------------- SEARCH ALGORITHMS ----------------

def naive_search(text, pattern, case_sensitive=False):
    if not pattern:
        return []

    if not case_sensitive:
        text = text.lower()
        pattern = pattern.lower()

    n = len(text)
    m = len(pattern)

    if m > n:
        return []

    positions = []

    for i in range(n - m + 1):
        if text[i:i + m] == pattern:
            positions.append(i)

    return positions


def kmp_search(text, pattern, case_sensitive=False):
    if not pattern:
        return []

    if not case_sensitive:
        text = text.lower()
        pattern = pattern.lower()

    lps = [0] * len(pattern)

    j = 0

    for i in range(1, len(pattern)):
        while j > 0 and pattern[i] != pattern[j]:
            j = lps[j - 1]

        if pattern[i] == pattern[j]:
            j += 1
            lps[i] = j

    positions = []
    i = 0
    j = 0

    while i < len(text):

        if text[i] == pattern[j]:
            i += 1
            j += 1

            if j == len(pattern):
                positions.append(i - j)
                j = lps[j - 1]

        elif j > 0:
            j = lps[j - 1]

        else:
            i += 1

    return positions


def rabin_karp_search(text, pattern, case_sensitive=False):
    if not pattern:
        return []

    if not case_sensitive:
        text = text.lower()
        pattern = pattern.lower()

    n = len(text)
    m = len(pattern)

    if m > n:
        return []

    base = 256
    prime = 1000003

    high = pow(base, m - 1, prime)

    pattern_hash = 0
    text_hash = 0

    for i in range(m):
        pattern_hash = (
            base * pattern_hash + ord(pattern[i])
        ) % prime

        text_hash = (
            base * text_hash + ord(text[i])
        ) % prime

    positions = []

    for i in range(n - m + 1):

        if pattern_hash == text_hash:

            if text[i:i + m] == pattern:
                positions.append(i)

        if i < n - m:
            text_hash = (
                base * (
                    text_hash
                    - ord(text[i]) * high
                )
                + ord(text[i + m])
            ) % prime

            text_hash %= prime

    return positions


def regex_search(text, pattern, case_sensitive=False, whole_word=False):
    flags = 0 if case_sensitive else re.IGNORECASE

    if whole_word:
        pattern = r"\b(?:" + pattern + r")\b"

    try:
        return list(re.finditer(pattern, text, flags))
    except re.error:
        return None


# ---------------- APPLICATION ----------------

class App:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "Real-Time Text Search & Pattern Matching Tool"
        )

        self.root.geometry("1350x850")
        self.root.minsize(1100, 720)

        self.history = []

        self.current_file = "Sample Text"

        self.positions = []

        self.match_ranges = []

        self.current_match = -1

        self.last_result = None

        self.search_job = None

        self.setup_style()

        self.build_ui()

        self.bind_shortcuts()

        self.load_sample()


    # ========================================================
    # STYLE
    # ========================================================

    def setup_style(self):

        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Title.TLabel",
            font=("Segoe UI", 22, "bold")
        )

        style.configure(
            "Subtitle.TLabel",
            font=("Segoe UI", 10)
        )

        style.configure(
            "Card.TLabel",
            font=("Segoe UI", 15, "bold")
        )

        style.configure(
            "Status.TLabel",
            font=("Segoe UI", 11, "bold")
        )

        style.configure(
            "TButton",
            font=("Segoe UI", 10),
            padding=7
        )

        style.configure(
            "Treeview",
            rowheight=27,
            font=("Segoe UI", 9)
        )

        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 9, "bold")
        )


    # ========================================================
    # UI
    # ========================================================

    def build_ui(self):

        # HEADER
        header = ttk.Frame(
            self.root,
            padding=(18, 10)
        )

        header.pack(fill="x")

        ttk.Label(
            header,
            text="REAL-TIME TEXT SEARCH & PATTERN MATCHING TOOL",
            style="Title.TLabel"
        ).pack()

        ttk.Label(
            header,
            text=(
                "Naive • KMP • Rabin-Karp • Regex   |   "
                "Advanced Text Analytics Dashboard"
            ),
            style="Subtitle.TLabel"
        ).pack(pady=3)


        # SEARCH CONTROLS

        controls = ttk.LabelFrame(
            self.root,
            text="Search Controls",
            padding=9
        )

        controls.pack(
            fill="x",
            padx=14,
            pady=5
        )


        ttk.Label(
            controls,
            text="Pattern:"
        ).grid(
            row=0,
            column=0,
            padx=4
        )


        self.query = tk.StringVar()

        self.entry = ttk.Entry(
            controls,
            textvariable=self.query,
            width=31
        )

        self.entry.grid(
            row=0,
            column=1,
            padx=4
        )

        self.entry.bind(
            "<KeyRelease>",
            self.schedule_realtime
        )


        ttk.Label(
            controls,
            text="Algorithm:"
        ).grid(
            row=0,
            column=2,
            padx=4
        )


        self.algorithm = tk.StringVar(
            value="KMP"
        )


        self.combo = ttk.Combobox(
            controls,
            textvariable=self.algorithm,
            values=[
                "Naive",
                "KMP",
                "Rabin-Karp",
                "Regex"
            ],
            state="readonly",
            width=13
        )

        self.combo.grid(
            row=0,
            column=3,
            padx=4
        )

        self.combo.bind(
            "<<ComboboxSelected>>",
            self.schedule_realtime
        )


        self.case_sensitive = tk.BooleanVar(
            value=False
        )

        self.whole_word = tk.BooleanVar(
            value=False
        )


        ttk.Checkbutton(
            controls,
            text="Case Sensitive",
            variable=self.case_sensitive,
            command=self.search
        ).grid(
            row=0,
            column=4,
            padx=5
        )


        ttk.Checkbutton(
            controls,
            text="Whole Word",
            variable=self.whole_word,
            command=self.search
        ).grid(
            row=0,
            column=5,
            padx=5
        )


        ttk.Button(
            controls,
            text="🔍 Search",
            command=self.search
        ).grid(
            row=0,
            column=6,
            padx=4
        )


        ttk.Button(
            controls,
            text="📂 Open File",
            command=self.load_file
        ).grid(
            row=0,
            column=7,
            padx=4
        )


        ttk.Button(
            controls,
            text="Clear",
            command=self.clear
        ).grid(
            row=0,
            column=8,
            padx=4
        )


        ttk.Button(
            controls,
            text="ℹ About",
            command=self.about
        ).grid(
            row=0,
            column=9,
            padx=4
        )


        # NAVIGATION

        nav = ttk.Frame(
            self.root,
            padding=(14, 2)
        )

        nav.pack(fill="x")


        ttk.Button(
            nav,
            text="◀ Previous Match",
            command=self.previous_match
        ).pack(side="left")


        ttk.Button(
            nav,
            text="Next Match ▶",
            command=self.next_match
        ).pack(
            side="left",
            padx=6
        )


        self.match_nav = ttk.Label(
            nav,
            text="No match selected"
        )

        self.match_nav.pack(
            side="left",
            padx=12
        )


        # DASHBOARD

        dash = ttk.Frame(
            self.root,
            padding=(12, 2)
        )

        dash.pack(fill="x")


        self.cards = {}


        for name in [
            "Characters",
            "Words",
            "Lines",
            "Matches",
            "Time (ms)",
            "Match %"
        ]:

            box = ttk.LabelFrame(
                dash,
                text=name,
                padding=7
            )

            box.pack(
                side="left",
                fill="x",
                expand=True,
                padx=3
            )


            label = ttk.Label(
                box,
                text="0",
                style="Card.TLabel",
                anchor="center"
            )

            label.pack(fill="x")

            self.cards[name] = label


        # MAIN AREA

        main = ttk.Panedwindow(
            self.root,
            orient="horizontal"
        )

        main.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=7
        )


        # TEXT AREA

        left = ttk.LabelFrame(
            main,
            text="Text Editor / Search Area",
            padding=5
        )

        main.add(
            left,
            weight=5
        )


        self.text = tk.Text(
            left,
            wrap="word",
            font=("Consolas", 11),
            undo=True,
            padx=8,
            pady=8
        )


        scroll = ttk.Scrollbar(
            left,
            orient="vertical",
            command=self.text.yview
        )


        self.text.configure(
            yscrollcommand=scroll.set
        )


        self.text.pack(
            side="left",
            fill="both",
            expand=True
        )


        scroll.pack(
            side="right",
            fill="y"
        )


        self.text.tag_configure(
            "match",
            background="yellow",
            foreground="black"
        )


        self.text.tag_configure(
            "current_match",
            background="orange",
            foreground="black"
        )


        # RIGHT SIDE

        right = ttk.Frame(
            main,
            padding=3
        )

        main.add(
            right,
            weight=3
        )


        # SEARCH RESULT

        result_box = ttk.LabelFrame(
            right,
            text="Search Result",
            padding=8
        )

        result_box.pack(
            fill="x",
            pady=(0, 7)
        )


        self.status = ttk.Label(
            result_box,
            text="Ready",
            style="Status.TLabel"
        )

        self.status.pack(
            anchor="w"
        )


        self.result = ttk.Label(
            result_box,
            text="Enter a pattern to search."
        )

        self.result.pack(
            anchor="w",
            pady=4
        )


        self.positions_label = ttk.Label(
            result_box,
            text="Positions: -",
            wraplength=390
        )

        self.positions_label.pack(
            anchor="w"
        )


        self.file_label = ttk.Label(
            result_box,
            text="File: Sample Text",
            wraplength=390
        )

        self.file_label.pack(
            anchor="w",
            pady=4
        )


        # ANALYTICS

        stats_box = ttk.LabelFrame(
            right,
            text="Text Analytics",
            padding=7
        )

        stats_box.pack(
            fill="x",
            pady=(0, 7)
        )


        self.stats_label = ttk.Label(
            stats_box,
            text="Statistics will appear here.",
            justify="left"
        )

        self.stats_label.pack(
            anchor="w"
        )


        # HISTORY

        hist_box = ttk.LabelFrame(
            right,
            text="Search History",
            padding=5
        )

        hist_box.pack(
            fill="both",
            expand=True
        )


        cols = (
            "time",
            "pattern",
            "algorithm",
            "matches",
            "ms"
        )


        self.history_tree = ttk.Treeview(
            hist_box,
            columns=cols,
            show="headings"
        )


        for c, h, w in [
            ("time", "Time", 60),
            ("pattern", "Pattern", 85),
            ("algorithm", "Algorithm", 85),
            ("matches", "Matches", 60),
            ("ms", "ms", 75)
        ]:

            self.history_tree.heading(
                c,
                text=h
            )

            self.history_tree.column(
                c,
                width=w,
                anchor="center"
            )


        self.history_tree.pack(
            fill="both",
            expand=True
        )


        # BOTTOM BUTTONS

        bottom = ttk.Frame(
            self.root,
            padding=(14, 0, 14, 9)
        )

        bottom.pack(fill="x")


        ttk.Button(
            bottom,
            text="📊 Compare Algorithms",
            command=self.compare
        ).pack(side="left")


        ttk.Button(
            bottom,
            text="📈 Performance Graph",
            command=self.performance_graph
        ).pack(
            side="left",
            padx=5
        )


        ttk.Button(
            bottom,
            text="📑 Export TXT",
            command=self.export_txt
        ).pack(
            side="left",
            padx=5
        )


        ttk.Button(
            bottom,
            text="📋 Export CSV",
            command=self.export_csv
        ).pack(
            side="left"
        )


        ttk.Button(
            bottom,
            text="🔤 Word Analysis",
            command=self.word_analysis
        ).pack(
            side="left",
            padx=5
        )


        ttk.Button(
            bottom,
            text="Load Sample",
            command=self.load_sample
        ).pack(
            side="left"
        )


        ttk.Button(
            bottom,
            text="Exit",
            command=self.root.destroy
        ).pack(
            side="right"
        )


        self.footer = ttk.Label(
            bottom,
            text="Ready"
        )

        self.footer.pack(
            side="right",
            padx=15
        )


    # ========================================================
    # KEYBOARD SHORTCUTS
    # ========================================================

    def bind_shortcuts(self):

        self.root.bind(
            "<Control-o>",
            lambda e: self.load_file()
        )

        self.root.bind(
            "<Control-f>",
            lambda e: self.focus_search()
        )

        self.root.bind(
            "<Escape>",
            lambda e: self.clear()
        )

        self.root.bind(
            "<F3>",
            lambda e: self.next_match()
        )

        self.root.bind(
            "<Shift-F3>",
            lambda e: self.previous_match()
        )


    def focus_search(self):

        self.entry.focus_set()

        self.entry.select_range(
            0,
            tk.END
        )


    # ========================================================
    # SAMPLE TEXT
    # ========================================================

    def sample_text(self):

        return """REAL-TIME TEXT SEARCH AND PATTERN MATCHING TOOL

Pattern matching is an important concept in computer science.
It is widely used in search engines, text editors, plagiarism detection,
cybersecurity applications and information retrieval systems.

The Naive String Matching algorithm checks every possible position.
The Knuth-Morris-Pratt algorithm, commonly called KMP, uses an LPS array.
The Rabin-Karp algorithm uses hashing to find matching patterns.
Regular expressions provide a powerful method for searching complex patterns.

Python is a popular programming language for text processing.
Python can be used for artificial intelligence and machine learning.
This project demonstrates real-time searching using Python and Tkinter.

Search engines use pattern matching to find relevant information.
Efficient algorithms reduce unnecessary character comparisons.
Fast searching improves user experience in large text collections.

Data structures and algorithms are important concepts in computer science.
Searching is one of the most common operations performed by computer programs.

Linear search checks items one after another.
Binary search repeatedly divides sorted data into smaller sections.
KMP improves pattern matching by avoiding unnecessary comparisons.
Rabin-Karp uses hashing for efficient pattern detection.

Natural language processing is another important application of text search.
NLP systems can analyze documents, sentences, words and patterns.
Sentiment analysis can classify text as positive, negative or neutral.

Machine learning uses data to learn useful patterns.
Classification, regression and clustering are common machine learning tasks.
Artificial intelligence is becoming increasingly important in modern technology.

A good search application should be fast, accurate and easy to use.
A graphical user interface allows users to search text without using commands.

This project includes multiple algorithms, real-time search,
case-sensitive searching, whole-word searching, match navigation,
text analytics, word frequency analysis, performance comparison,
search history and report export.

The main objective is to demonstrate how searching algorithms
can be implemented and compared using a practical Python application.
"""


    # ========================================================
    # FILE OPERATIONS
    # ========================================================

    def load_sample(self):

        self.text.delete(
            "1.0",
            tk.END
        )

        self.text.insert(
            "1.0",
            self.sample_text()
        )

        self.current_file = "Sample Text"

        self.file_label.config(
            text="File: Sample Text"
        )

        self.clear(
            reset_query=False
        )

        self.update_text_stats()


    def load_file(self):

        path = filedialog.askopenfilename(
            title="Select Text File",
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )

        if not path:
            return


        try:

            try:

                with open(
                    path,
                    "r",
                    encoding="utf-8"
                ) as f:

                    content = f.read()

            except UnicodeDecodeError:

                with open(
                    path,
                    "r",
                    encoding="cp1252"
                ) as f:

                    content = f.read()


            self.text.delete(
                "1.0",
                tk.END
            )

            self.text.insert(
                "1.0",
                content
            )


            self.current_file = path


            self.file_label.config(
                text=f"File: {os.path.basename(path)}"
            )


            self.clear(
                reset_query=False
            )

            self.update_text_stats()

            self.footer.config(
                text="File loaded successfully"
            )


        except Exception as e:

            messagebox.showerror(
                "File Error",
                str(e)
            )


    # ========================================================
    # SEARCH
    # ========================================================

    def schedule_realtime(self, event=None):

        if self.search_job:

            try:

                self.root.after_cancel(
                    self.search_job
                )

            except Exception:
                pass


        self.search_job = self.root.after(
            180,
            self.search
        )


    def search(self):

        self.search_job = None

        pattern = self.query.get()

        text = self.text.get(
            "1.0",
            "end-1c"
        )


        self.update_text_stats()


        if not pattern:

            self.clear(
                reset_query=False
            )

            return


        algorithm = self.algorithm.get()

        case_sensitive = self.case_sensitive.get()

        whole_word = self.whole_word.get()


        start = time.perf_counter()


        # ----------------------------------------------------
        # REGEX
        # ----------------------------------------------------

        if algorithm == "Regex":

            matches = regex_search(
                text,
                pattern,
                case_sensitive,
                whole_word
            )


            if matches is None:

                self.show_invalid_regex()

                return


            match_ranges = [
                (m.start(), m.end())
                for m in matches
            ]

            positions = [
                m.start()
                for m in matches
            ]


        # ----------------------------------------------------
        # NORMAL ALGORITHMS
        # ----------------------------------------------------

        else:

            if whole_word:

                escaped = re.escape(pattern)

                flags = (
                    0
                    if case_sensitive
                    else re.IGNORECASE
                )

                actual_matches = list(
                    re.finditer(
                        r"\b" + escaped + r"\b",
                        text,
                        flags
                    )
                )

                positions = [
                    m.start()
                    for m in actual_matches
                ]

                match_ranges = [
                    (m.start(), m.end())
                    for m in actual_matches
                ]

            else:

                if algorithm == "Naive":

                    positions = naive_search(
                        text,
                        pattern,
                        case_sensitive
                    )

                elif algorithm == "KMP":

                    positions = kmp_search(
                        text,
                        pattern,
                        case_sensitive
                    )

                else:

                    positions = rabin_karp_search(
                        text,
                        pattern,
                        case_sensitive
                    )


                match_ranges = [
                    (
                        p,
                        p + len(pattern)
                    )
                    for p in positions
                ]


        elapsed = (
            time.perf_counter() - start
        ) * 1000


        self.positions = positions

        self.match_ranges = match_ranges

        self.current_match = (
            0 if positions else -1
        )


        self.last_result = {

            "pattern": pattern,

            "algorithm": algorithm,

            "matches": len(positions),

            "elapsed": elapsed,

            "positions": positions[:],

            "ranges": match_ranges[:]

        }


        self.highlight(
            match_ranges
        )


        matches_count = len(positions)


        # Match percentage

        matched_chars = sum(
            end - start
            for start, end in match_ranges
        )


        percent = min(
            100,
            (
                matched_chars /
                max(1, len(text))
            ) * 100
        )


        # STATUS

        if matches_count:

            self.status.config(
                text="✓ MATCH FOUND"
            )

        else:

            self.status.config(
                text="✗ NO MATCH FOUND"
            )


        self.result.config(
            text=(
                f"{algorithm}  |  "
                f"{matches_count:,} match(es)"
            )
        )


        # Positions

        if positions:

            p = ", ".join(
                map(str, positions[:50])
            )

            if len(positions) > 50:

                p += " ..."

        else:

            p = "-"


        self.positions_label.config(
            text=f"Positions: {p}"
        )


        # Cards

        self.cards["Matches"].config(
            text=f"{matches_count:,}"
        )

        self.cards["Time (ms)"].config(
            text=f"{elapsed:.6f}"
        )

        self.cards["Match %"].config(
            text=f"{percent:.2f}%"
        )


        # Navigation

        if positions:

            self.match_nav.config(
                text=(
                    f"Match "
                    f"{self.current_match + 1} "
                    f"of "
                    f"{len(positions)}"
                )
            )

        else:

            self.match_nav.config(
                text="No match selected"
            )


        self.footer.config(
            text="Search completed"
        )


        self.add_history(
            pattern,
            algorithm,
            matches_count,
            elapsed
        )


        if positions:

            self.select_match(
                self.current_match
            )


    # ========================================================
    # HIGHLIGHTING
    # ========================================================

    def highlight(self, match_ranges):

        self.text.tag_remove(
            "match",
            "1.0",
            tk.END
        )

        self.text.tag_remove(
            "current_match",
            "1.0",
            tk.END
        )


        for start, end in match_ranges:

            self.text.tag_add(
                "match",
                f"1.0 + {start} chars",
                f"1.0 + {end} chars"
            )


    def select_match(self, index):

        if not self.match_ranges:
            return


        if (
            index < 0
            or index >= len(self.match_ranges)
        ):
            return


        self.text.tag_remove(
            "current_match",
            "1.0",
            tk.END
        )


        start_pos, end_pos = (
            self.match_ranges[index]
        )


        start = (
            f"1.0 + {start_pos} chars"
        )

        end = (
            f"1.0 + {end_pos} chars"
        )


        self.text.tag_add(
            "current_match",
            start,
            end
        )


        self.text.see(start)


        self.match_nav.config(
            text=(
                f"Match {index + 1} "
                f"of {len(self.match_ranges)}"
            )
        )


    # ========================================================
    # NAVIGATION
    # ========================================================

    def next_match(self):

        if not self.positions:
            return


        self.current_match = (
            self.current_match + 1
        ) % len(self.positions)


        self.select_match(
            self.current_match
        )


    def previous_match(self):

        if not self.positions:
            return


        self.current_match = (
            self.current_match - 1
        ) % len(self.positions)


        self.select_match(
            self.current_match
        )


    # ========================================================
    # CLEAR
    # ========================================================

    def clear(self, reset_query=True):

        if reset_query:

            self.query.set("")


        self.text.tag_remove(
            "match",
            "1.0",
            tk.END
        )

        self.text.tag_remove(
            "current_match",
            "1.0",
            tk.END
        )


        self.positions = []

        self.match_ranges = []

        self.current_match = -1

        self.last_result = None


        text = self.text.get(
            "1.0",
            "end-1c"
        )


        self.cards["Characters"].config(
            text=f"{len(text):,}"
        )

        self.cards["Words"].config(
            text=f"{len(text.split()):,}"
        )

        self.cards["Lines"].config(
            text=f"{len(text.splitlines()):,}"
        )

        self.cards["Matches"].config(
            text="0"
        )

        self.cards["Time (ms)"].config(
            text="0"
        )

        self.cards["Match %"].config(
            text="0%"
        )


        self.status.config(
            text="READY"
        )


        self.result.config(
            text="Enter a pattern to search."
        )


        self.positions_label.config(
            text="Positions: -"
        )


        self.match_nav.config(
            text="No match selected"
        )


        self.footer.config(
            text="Ready"
        )


    # ========================================================
    # INVALID REGEX
    # ========================================================

    def show_invalid_regex(self):

        self.text.tag_remove(
            "match",
            "1.0",
            tk.END
        )

        self.text.tag_remove(
            "current_match",
            "1.0",
            tk.END
        )


        self.positions = []

        self.match_ranges = []

        self.current_match = -1


        self.status.config(
            text="⚠ INVALID REGULAR EXPRESSION"
        )


        self.result.config(
            text="Please correct the search pattern."
        )


        self.positions_label.config(
            text="Positions: -"
        )


        self.match_nav.config(
            text="No match selected"
        )


    # ========================================================
    # TEXT ANALYTICS
    # ========================================================

    def update_text_stats(self):

        text = self.text.get(
            "1.0",
            "end-1c"
        )


        words = re.findall(
            r"\b[\w']+\b",
            text.lower()
        )


        unique = len(
            set(words)
        )


        sentences = len(
            re.findall(
                r"[.!?]+(?:\s|$)",
                text
            )
        )


        avg_word = (

            sum(
                map(len, words)
            )
            /
            len(words)

            if words
            else 0
        )


        self.cards["Characters"].config(
            text=f"{len(text):,}"
        )


        self.cards["Words"].config(
            text=f"{len(words):,}"
        )


        self.cards["Lines"].config(
            text=f"{len(text.splitlines()):,}"
        )


        self.stats_label.config(

            text=(
                f"Characters: {len(text):,}\n"
                f"Words: {len(words):,}   |   "
                f"Unique: {unique:,}\n"
                f"Lines: {len(text.splitlines()):,}   |   "
                f"Sentences: {sentences:,}\n"
                f"Average word length: "
                f"{avg_word:.2f} characters"
            )
        )


    # ========================================================
    # WORD ANALYSIS
    # ========================================================

    def word_analysis(self):

        text = self.text.get(
            "1.0",
            "end-1c"
        )


        words = re.findall(
            r"\b[\w']+\b",
            text.lower()
        )


        counts = Counter(words)


        w = tk.Toplevel(
            self.root
        )

        w.title(
            "Word Frequency Analysis"
        )

        w.geometry(
            "620x560"
        )


        ttk.Label(
            w,
            text="Word Frequency Analysis",
            font=("Segoe UI", 17, "bold")
        ).pack(
            pady=12
        )


        ttk.Label(
            w,
            text=(
                f"Total words: {len(words):,} | "
                f"Unique words: {len(counts):,}"
            )
        ).pack()


        tree = ttk.Treeview(
            w,
            columns=(
                "rank",
                "word",
                "count"
            ),
            show="headings",
            height=18
        )


        for c, h, width in [
            ("rank", "Rank", 70),
            ("word", "Word", 300),
            ("count", "Frequency", 120)
        ]:

            tree.heading(
                c,
                text=h
            )

            tree.column(
                c,
                width=width,
                anchor="center"
            )


        tree.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=15
        )


        for rank, (
            word,
            count
        ) in enumerate(
            counts.most_common(20),
            1
        ):

            tree.insert(
                "",
                tk.END,
                values=(
                    rank,
                    word,
                    count
                )
            )


        ttk.Button(
            w,
            text="Close",
            command=w.destroy
        ).pack(
            pady=8
        )


    # ========================================================
    # ALGORITHM COMPARISON
    # ========================================================

    def compare_data(self):

        text = self.text.get(
            "1.0",
            "end-1c"
        )


        pattern = self.query.get()


        if not pattern:
            return []


        rows = []


        algorithms = [
            ("Naive", naive_search),
            ("KMP", kmp_search),
            ("Rabin-Karp", rabin_karp_search)
        ]


        for name, func in algorithms:

            start = time.perf_counter()


            positions = func(
                text,
                pattern,
                self.case_sensitive.get()
            )


            elapsed = (
                time.perf_counter()
                - start
            ) * 1000


            rows.append(
                (
                    name,
                    len(positions),
                    elapsed
                )
            )


        return rows


    def compare(self):

        pattern = self.query.get()


        if not pattern:

            messagebox.showwarning(
                "Pattern Required",
                "Enter a pattern first."
            )

            return


        rows = self.compare_data()


        w = tk.Toplevel(
            self.root
        )

        w.title(
            "Algorithm Performance Comparison"
        )

        w.geometry(
            "760x500"
        )


        ttk.Label(
            w,
            text="Algorithm Performance Comparison",
            font=("Segoe UI", 17, "bold")
        ).pack(
            pady=12
        )


        ttk.Label(
            w,
            text=(
                f"Pattern: {pattern} | "
                f"Text: "
                f"{len(self.text.get('1.0', 'end-1c')):,} "
                f"characters"
            )
        ).pack()


        tree = ttk.Treeview(
            w,
            columns=(
                "algorithm",
                "matches",
                "time",
                "complexity"
            ),
            show="headings",
            height=8
        )


        for c, h, width in [
            ("algorithm", "Algorithm", 160),
            ("matches", "Matches", 100),
            ("time", "Time (ms)", 140),
            ("complexity", "Worst-case", 190)
        ]:

            tree.heading(
                c,
                text=h
            )

            tree.column(
                c,
                width=width,
                anchor="center"
            )


        tree.pack(
            fill="x",
            padx=20,
            pady=20
        )


        complexity = {

            "Naive":
                "O(n × m)",

            "KMP":
                "O(n + m)",

            "Rabin-Karp":
                "O(n × m)"
        }


        for name, matches, elapsed in rows:

            tree.insert(
                "",
                tk.END,
                values=(
                    name,
                    matches,
                    f"{elapsed:.6f}",
                    complexity[name]
                )
            )


        fastest = min(
            rows,
            key=lambda x: x[2]
        )


        ttk.Label(
            w,
            text=(
                f"Fastest in this test: "
                f"{fastest[0]} "
                f"({fastest[2]:.6f} ms)"
            ),
            font=("Segoe UI", 11, "bold")
        ).pack(
            pady=5
        )


        ttk.Button(
            w,
            text="Close",
            command=w.destroy
        ).pack(
            pady=10
        )


    # ========================================================
    # PERFORMANCE GRAPH
    # ========================================================

    def performance_graph(self):

        pattern = self.query.get()


        if not pattern:

            messagebox.showwarning(
                "Pattern Required",
                "Enter a pattern first."
            )

            return


        rows = self.compare_data()


        w = tk.Toplevel(
            self.root
        )

        w.title(
            "Algorithm Performance Graph"
        )

        w.geometry(
            "760x560"
        )


        ttk.Label(
            w,
            text="Execution Time Comparison",
            font=("Segoe UI", 17, "bold")
        ).pack(
            pady=10
        )


        canvas = tk.Canvas(
            w,
            width=700,
            height=390,
            bg="white",
            highlightthickness=1
        )

        canvas.pack(
            padx=20,
            pady=10
        )


        max_time = max(
            [r[2] for r in rows] + [0.001]
        )


        chart_left = 80

        chart_top = 40

        chart_bottom = 330

        chart_right = 660


        canvas.create_line(
            chart_left,
            chart_top,
            chart_left,
            chart_bottom,
            width=2
        )


        canvas.create_line(
            chart_left,
            chart_bottom,
            chart_right,
            chart_bottom,
            width=2
        )


        for i in range(5):

            y = (
                chart_bottom
                -
                i * (
                    (chart_bottom - chart_top)
                    / 4
                )
            )


            value = (
                max_time * i / 4
            )


            canvas.create_line(
                chart_left,
                y,
                chart_right,
                y,
                fill="#dddddd"
            )


            canvas.create_text(
                chart_left - 35,
                y,
                text=f"{value:.3f}",
                font=("Segoe UI", 8)
            )


        bar_width = 65

        gap = 45


        for i, (
            name,
            matches,
            elapsed
        ) in enumerate(rows):

            x1 = (
                chart_left
                +
                55
                +
                i * (
                    bar_width + gap
                )
            )


            x2 = (
                x1
                +
                bar_width
            )


            height = (
                elapsed
                /
                max_time
            ) * (
                chart_bottom
                -
                chart_top
            )


            y1 = (
                chart_bottom
                -
                height
            )


            canvas.create_rectangle(
                x1,
                y1,
                x2,
                chart_bottom,
                fill="#6c8ebf"
            )


            canvas.create_text(
                (x1 + x2) / 2,
                chart_bottom + 18,
                text=name,
                font=("Segoe UI", 9)
            )


            canvas.create_text(
                (x1 + x2) / 2,
                max(
                    20,
                    y1 - 10
                ),
                text=f"{elapsed:.4f} ms",
                font=("Segoe UI", 8)
            )


        ttk.Label(
            w,
            text="Lower bar = faster execution time"
        ).pack()


        ttk.Button(
            w,
            text="Close",
            command=w.destroy
        ).pack(
            pady=8
        )


    # ========================================================
    # HISTORY
    # ========================================================

    def add_history(
        self,
        pattern,
        algorithm,
        matches,
        elapsed
    ):

        item = (
            datetime.now().strftime(
                "%H:%M:%S"
            ),
            pattern,
            algorithm,
            matches,
            f"{elapsed:.6f}"
        )


        if (
            self.history
            and
            self.history[-1][1:]
            == item[1:]
        ):

            return


        self.history.append(
            item
        )


        self.history_tree.insert(
            "",
            0,
            values=item
        )


    # ========================================================
    # EXPORT TXT
    # ========================================================

    def export_txt(self):

        if not self.last_result:

            messagebox.showwarning(
                "No Result",
                "Perform a search before exporting."
            )

            return


        path = filedialog.asksaveasfilename(
            title="Export Search Report",
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt")
            ]
        )


        if not path:
            return


        text = self.text.get(
            "1.0",
            "end-1c"
        )


        result = self.last_result


        report = [

            "REAL-TIME TEXT SEARCH & PATTERN MATCHING TOOL",

            "=" * 60,

            f"Generated: "
            f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",

            f"File: {self.current_file}",

            f"Algorithm: {result['algorithm']}",

            f"Pattern: {result['pattern']}",

            f"Case Sensitive: "
            f"{self.case_sensitive.get()}",

            f"Whole Word: "
            f"{self.whole_word.get()}",

            f"Characters: {len(text):,}",

            f"Words: {len(text.split()):,}",

            f"Matches: {result['matches']:,}",

            f"Execution Time: "
            f"{result['elapsed']:.6f} ms",

            "Positions: "
            +
            ", ".join(
                map(
                    str,
                    result["positions"]
                )
            ),

            "",

            "Project: Real-Time Text Search and Pattern Matching Tool",

            "Technology: Python + Tkinter"

        ]


        try:

            with open(
                path,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(
                    "\n".join(report)
                )


            messagebox.showinfo(
                "Export Complete",
                f"Report saved:\n{path}"
            )


        except Exception as e:

            messagebox.showerror(
                "Export Error",
                str(e)
            )


    # ========================================================
    # EXPORT CSV
    # ========================================================

    def export_csv(self):

        if not self.history:

            messagebox.showwarning(
                "No History",
                "Perform at least one search first."
            )

            return


        path = filedialog.asksaveasfilename(
            title="Export Search History",
            defaultextension=".csv",
            filetypes=[
                ("CSV files", "*.csv")
            ]
        )


        if not path:
            return


        try:

            with open(
                path,
                "w",
                newline="",
                encoding="utf-8"
            ) as f:

                writer = csv.writer(f)


                writer.writerow(
                    [
                        "Time",
                        "Pattern",
                        "Algorithm",
                        "Matches",
                        "Execution Time (ms)"
                    ]
                )


                writer.writerows(
                    self.history
                )


            messagebox.showinfo(
                "Export Complete",
                f"CSV saved:\n{path}"
            )


        except Exception as e:

            messagebox.showerror(
                "Export Error",
                str(e)
            )


    # ========================================================
    # ABOUT
    # ========================================================

    def about(self):

        messagebox.showinfo(

            "About Project",

            "REAL-TIME TEXT SEARCH & PATTERN MATCHING TOOL\n\n"

            "Advanced B.Tech Project\n\n"

            "SEARCH ALGORITHMS\n"
            "• Naive String Matching\n"
            "• Knuth-Morris-Pratt (KMP)\n"
            "• Rabin-Karp\n"
            "• Regular Expressions\n\n"

            "FEATURES\n"
            "• Real-time searching\n"
            "• Case-sensitive searching\n"
            "• Whole-word searching\n"
            "• Regex searching\n"
            "• Match highlighting\n"
            "• Match navigation\n"
            "• Text analytics\n"
            "• Word frequency analysis\n"
            "• Algorithm comparison\n"
            "• Performance graph\n"
            "• Search history\n"
            "• TXT report export\n"
            "• CSV history export\n"
            "• Text-file loading\n"
            "• Keyboard shortcuts\n\n"

            "SHORTCUTS\n"
            "Ctrl + O  → Open File\n"
            "Ctrl + F  → Search Box\n"
            "F3       → Next Match\n"
            "Shift+F3 → Previous Match\n"
            "Esc      → Clear Search\n\n"

            "Technology: Python + Tkinter\n"
            "Version: 3.0"
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = App(root)

    root.mainloop()
