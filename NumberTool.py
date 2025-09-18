import tkinter as tk
from tkinter import messagebox
from fractions import Fraction
from decimal import Decimal, InvalidOperation
import math
import re

# ---------- parsing / math utilities ----------
def parse_number(num_str):
    """Convert a number string (decimal, fraction, percent, whole, or mixed like '-3 6/7') to Fraction."""
    s = num_str.strip()
    if not s:
        raise ValueError("Empty number")
    try:
        if s.endswith('%'):
            val = Decimal(s[:-1])
            return Fraction(val / Decimal(100))
        if ' ' in s and '/' in s:
            parts = s.split()
            if len(parts) == 2:
                whole_str, frac_str = parts
                sign = -1 if whole_str.startswith('-') else 1
                whole = int(whole_str.lstrip('+-'))
                num_str2, den_str = frac_str.split('/', 1)
                num = int(num_str2)
                den = int(den_str)
                if den == 0:
                    raise ZeroDivisionError("Denominator cannot be zero")
                return Fraction(sign * (whole * den + num), den)
        if '/' in s:
            return Fraction(s)
        try:
            d = Decimal(s)
            return Fraction(d)
        except InvalidOperation:
            return Fraction(float(s))
    except (ValueError, ZeroDivisionError, InvalidOperation) as e:
        raise ValueError(f"Invalid number: {num_str}") from e
#calc
def calc_click(char):
    if char == "C":
        calc_display.delete(0, tk.END)
    elif char == "=":
        try:
            expr = calc_display.get()
            result = eval(expr, {"__builtins__": None}, {})
            calc_display.delete(0, tk.END)
            calc_display.insert(tk.END, str(result))
        except Exception:
            messagebox.showerror("Error", "Invalid Expression")
    else:
        calc_display.insert(tk.END, char)



#mmr 
def calculate_stats(numbers):
    """numbers: list of strings; returns (mean, median, range) as Fractions"""
    nums = [parse_number(n) for n in numbers if n.strip()]
    if not nums:
        raise ValueError("No valid numbers to calculate stats.")

    nums_sorted = sorted(nums)
    n = len(nums)

    # mean
    mean_val = sum(nums) / n

    # median
    mid = n // 2
    if n % 2 == 1:
        median_val = nums_sorted[mid]
    else:
        median_val = (nums_sorted[mid - 1] + nums_sorted[mid]) / 2

    # range
    range_val = nums_sorted[-1] - nums_sorted[0]

    return mean_val, median_val, range_val



def sort_numbers(numbers, reverse=False):
    """Sort list of number strings in ascending or descending order.
    Preserve the original (unsimplified) string representation in the output.
    """
    parsed = []
    for n in numbers:
        orig = n.strip()
        if orig == "":
            continue
        val = parse_number(orig)
        parsed.append((val, orig))
    parsed.sort(key=lambda t: t[0], reverse=reverse)
    return [t[1] for t in parsed]

def fraction_to_decimal_str(frac: Fraction):
    dec = Decimal(frac.numerator) / Decimal(frac.denominator)
    s = format(dec, 'f')
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    return s

def fraction_to_percent_str(frac: Fraction):
    dec = Decimal(frac.numerator) / Decimal(frac.denominator)
    percent = dec * Decimal(100)
    s = format(percent, 'f')
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    return s + '%'

# ---------- UI actions ----------
def on_sort():
    input_text = entry.get()
    if not input_text.strip():
        messagebox.showwarning("Input Error", "Please enter some numbers separated by commas.")
        return
    numbers = input_text.split(',')
    try:
        least_to_greatest = sort_numbers(numbers)
        greatest_to_least = sort_numbers(numbers, reverse=True)
        result_ltog.config(text=", ".join(least_to_greatest))
        result_gtol.config(text=", ".join(greatest_to_least))
    except ValueError as e:
        messagebox.showerror("Input Error", str(e))

def on_convert():
    s = convert_entry.get()
    if not s.strip():
        messagebox.showwarning("Input Error", "Please enter a number to convert.")
        return
    try:
        frac = parse_number(s)
        conv_frac.config(text=str(frac))
        conv_decimal.config(text=fraction_to_decimal_str(frac))
        conv_percent.config(text=fraction_to_percent_str(frac))
    except ValueError as e:
        messagebox.showerror("Input Error", str(e))

def on_sqrt():
    s = sqrt_entry.get().strip()
    if not s:
        messagebox.showwarning("Input Error", "Enter a number to take the square root of.")
        return
    try:
        frac = parse_number(s)
        val = float(frac.numerator) / float(frac.denominator)
        if val < 0:
            messagebox.showerror("Math Error", "Cannot take square root of a negative number.")
            return
        root = math.sqrt(val)
        if abs(root - round(root)) < 1e-12:
            root_str = str(int(round(root)))
        else:
            root_str = f"{root:.12g}"
        sqrt_result.config(text=root_str)
    except ValueError as e:
        messagebox.showerror("Input Error", str(e))

# Exponent rule (symbolic only)
def format_exp(frac: Fraction):
    if frac.denominator == 1:
        return str(frac.numerator)
    return f"{frac.numerator}/{frac.denominator}"

def try_parse_exponent(es):
    es = es.strip()
    if es == "":
        raise ValueError("Exponent is empty")
    return parse_number(es)

def on_exponent_rule():
    base_text = base_entry.get().strip()
    e1_text = exp1_entry.get().strip()
    e2_text = exp2_entry.get().strip()
    rule_label = rule_var.get()
    if not base_text:
        from tkinter import messagebox
        messagebox.showwarning("Input Error", "Enter a base (number or symbol).")
        return
    try:
        rule_code = rules_map[rule_label]

        # NEW: Negative exponent rule (uses exponent 1 if present, otherwise exponent 2)
        if rule_code == "negative_exponent":
            es = e1_text or e2_text
            if not es:
                messagebox.showwarning("Input Error", "Enter an exponent (negative integer).")
                return
            e = try_parse_exponent(es)
            # require a negative integer (denominator == 1 and numerator < 0)
            if e.denominator != 1 or e.numerator >= 0:
                messagebox.showwarning("Input Error", "Exponent must be a negative integer for this rule.")
                return
            pos = Fraction(-e.numerator, 1)
            expr = f"{base_text}^{format_exp(e)} = 1/{base_text}^{format_exp(pos)}"
            result_expr.config(text=expr)
            result_numeric.config(text="(symbolic only)")
            return

        # existing symbolic rules (unchanged)
        e1 = try_parse_exponent(e1_text)
        e2 = try_parse_exponent(e2_text)

        if rule_code == "power_of_power":
            result_exp = e1 * e2
            expr = f"({base_text}^{format_exp(e1)})^{format_exp(e2)} = {base_text}^{format_exp(result_exp)}"
        elif rule_code == "multiply_same_base":
            result_exp = e1 + e2
            expr = f"{base_text}^{format_exp(e1)} * {base_text}^{format_exp(e2)} = {base_text}^{format_exp(result_exp)}"
        elif rule_code == "divide_same_base":
            result_exp = e1 - e2
            expr = f"{base_text}^{format_exp(e1)} / {base_text}^{format_exp(e2)} = {base_text}^{format_exp(result_exp)}"
        else:
            expr = "Unknown rule"

        result_expr.config(text=expr)
        result_numeric.config(text="(symbolic only)")
    except ValueError as e:
        messagebox.showerror("Input Error", str(e))

# --- NEW: Evaluate numeric result button handler ---
def on_exponent_evaluate():
    base_text = base_entry.get().strip()
    e1_text = exp1_entry.get().strip()
    e2_text = exp2_entry.get().strip()
    rule_label = rule_var.get()
    if not base_text:
        messagebox.showwarning("Input Error", "Enter a base (number or symbol).")
        return
    try:
        rule_code = rules_map[rule_label]

        # attempt to parse base as numeric Fraction
        try:
            base_frac = parse_number(base_text)
            base_num = float(base_frac.numerator) / float(base_frac.denominator)
            base_is_numeric = True
        except ValueError:
            base_is_numeric = False

        # Negative exponent numeric evaluation
        if rule_code == "negative_exponent":
            es = e1_text or e2_text
            if not es:
                messagebox.showwarning("Input Error", "Enter an exponent (negative integer).")
                return
            e = try_parse_exponent(es)
            if e.denominator != 1 or e.numerator >= 0:
                messagebox.showwarning("Input Error", "Exponent must be a negative integer for this rule.")
                return
            if not base_is_numeric:
                result_numeric.config(text="(symbolic only)")
                return
            try:
                numeric = base_num ** float(e)  # e is negative integer
                result_numeric.config(text=f"{numeric:.12g}")
            except Exception as ex:
                messagebox.showerror("Math Error", str(ex))
            return

        # parse both exponents for other rules
        e1 = try_parse_exponent(e1_text)
        e2 = try_parse_exponent(e2_text)

        if rule_code == "power_of_power":
            res_exp = e1 * e2
        elif rule_code == "multiply_same_base":
            res_exp = e1 + e2
        elif rule_code == "divide_same_base":
            res_exp = e1 - e2
        else:
            messagebox.showerror("Input Error", "Unknown rule.")
            return

        if not base_is_numeric:
            result_numeric.config(text="(symbolic only)")
            return

        # numeric evaluation (use float for fractional exponents)
        try:
            numeric = base_num ** float(res_exp)
            result_numeric.config(text=f"{numeric:.12g}")
        except ZeroDivisionError:
            messagebox.showerror("Math Error", "Division by zero in exponent evaluation.")
        except Exception as ex:
            messagebox.showerror("Math Error", str(ex))

    except ValueError as e:
        messagebox.showerror("Input Error", str(e))

# ---------- Algebraic (linear) solver ----------
def _parse_side_for_var(side: str, var: str):
    """Return (coeff_sum: Fraction, const_sum: Fraction) for expression side."""
    side = side.replace('−', '-').replace(' ', '')  # normalize
    if side == '':
        return Fraction(0), Fraction(0)
    tokens = re.findall(r'[+-]?[^+-]+', side)
    coeff_sum = Fraction(0)
    const_sum = Fraction(0)
    for t in tokens:
        if var in t:
            # coefficient token e.g. '3x', '-x', '3/2x'
            coeff_str = t.replace(var, '')
            if coeff_str in ('', '+'):
                coeff = Fraction(1)
            elif coeff_str == '-':
                coeff = Fraction(-1)
            else:
                coeff = parse_number(coeff_str)
            coeff_sum += coeff
        else:
            # constant term
            const_sum += parse_number(t)
    return coeff_sum, const_sum

def solve_linear_equation(equation: str):
    """
    Solve linear equation in one variable.
    Supports formats like:
      2x+3=7
      -3 1/2x + 4 = x/2 + 1
      3/4x - 2 = -1/2 x + 5/3
    Returns tuple (status, message, solution_fraction or None)
    status: 'unique', 'infinite', 'none', 'error'
    """
    try:
        eq = equation.strip().replace(' ', '')
        if '=' not in eq:
            return 'error', "Equation must contain '='.", None
        left, right = eq.split('=', 1)
        # detect variable (first alpha char)
        m = re.search(r'[A-Za-z]', equation)
        if not m:
            return 'error', "No variable found in equation.", None
        var = m.group(0)
        a_left, b_left = _parse_side_for_var(left, var)
        a_right, b_right = _parse_side_for_var(right, var)
        # bring to form (a_left - a_right) * var = (b_right - b_left)
        a = a_left - a_right
        b = b_right - b_left
        if a == 0:
            if b == 0:
                return 'infinite', "Infinite solutions (identity).", None
            else:
                return 'none', "No solution.", None
        solution = Fraction(b, a)  # exact rational
        return 'unique', f"{var} = {solution}", solution
    except Exception as ex:
        return 'error', f"Parse error: {ex}", None

def on_solve_algebra():
    eq = alg_entry.get().strip()
    if not eq:
        messagebox.showwarning("Input Error", "Enter an equation to solve (e.g. 2x+3=7).")
        return
    status, msg, sol = solve_linear_equation(eq)
    alg_result.config(text=msg)
    if status == 'unique' and sol is not None:
        try:
            alg_result_decimal.config(text=f"{float(sol):.12g}")
        except Exception:
            alg_result_decimal.config(text="")
    else:
        alg_result_decimal.config(text="")

# ---------- Theme support ----------
light_theme = {
    "bg": "#f0f4f8",
    "fg": "#0b2447",
    "entry_bg": "#ffffff",
    "button_bg": "#1976d2",    # light blue buttons
    "button_fg": "#ffffff",
    "accent": "#0b5ed7",
    "result_bg": "#ffffff",
}
dark_theme = {
    "bg": "#3D3D3D",            # requested dark background for entire page
    "fg": "#A3A3A3",           # light grey text
    "entry_bg": "#3D3D3D",     # match page background (not just text boxes)
    "button_bg": "#3a3a3a",    # dark grey buttons
    "button_fg": "#ff8c00",    # orange text on dark mode buttons
    "accent": "#ff8c00",
    "result_bg": "#3D3D3D",    # result areas same as page background
}

widget_groups = {
    "labels": [],
    "entries": [],
    "buttons": [],
    "optionmenus": [],
}

is_dark = False

def apply_theme(theme):
    root.configure(bg=theme["bg"])
    # canvas and scrollable_frame if present
    if "canvas" in globals():
        try:
            canvas.configure(bg=theme["bg"])
        except Exception:
            pass
    if "scrollable_frame" in globals():
        try:
            scrollable_frame.configure(bg=theme["bg"])
        except Exception:
            pass

    # apply to known grouped widgets (keeps compatibility)
    for lbl in widget_groups["labels"]:
        try:
            lbl.configure(bg=theme["bg"], fg=theme["fg"])
        except Exception:
            pass
    for ent in widget_groups["entries"]:
        try:
            ent.configure(bg=theme["entry_bg"], fg=theme["fg"], insertbackground=theme["fg"])
        except Exception:
            pass
    for btn in widget_groups["buttons"]:
        try:
            btn.configure(bg=theme["button_bg"], fg=theme["button_fg"], activebackground=theme["accent"], relief="raised")
        except Exception:
            pass
    for om in widget_groups["optionmenus"]:
        try:
            om.configure(bg=theme["button_bg"], fg=theme["button_fg"], activebackground=theme["accent"])
            om["menu"].configure(bg=theme["entry_bg"], fg=theme["fg"])
        except Exception:
            pass

    # Recursively apply background/foreground to all child widgets so entire page uses theme.bg
    def _recurse_apply(w):
        try:
            cls = w.winfo_class()
            if cls in ("Frame", "Labelframe"):
                w.configure(bg=theme["bg"])
            elif cls == "Canvas":
                w.configure(bg=theme["bg"])
            elif cls == "Label":
                w.configure(bg=theme["bg"], fg=theme["fg"])
            elif cls == "Entry" or cls == "Text":
                w.configure(bg=theme["entry_bg"], fg=theme["fg"], insertbackground=theme["fg"])
            elif cls == "Button":
                w.configure(bg=theme["button_bg"], fg=theme["button_fg"], activebackground=theme["accent"])
            elif cls == "Scrollbar":
                # some platforms accept troughcolor, background, etc.
                try:
                    w.configure(bg=theme["bg"], troughcolor=theme.get("entry_bg", theme["bg"]))
                except Exception:
                    try:
                        w.configure(bg=theme["bg"])
                    except Exception:
                        pass
            elif cls == "Menubutton":
                try:
                    w.configure(bg=theme["button_bg"], fg=theme["button_fg"])
                    # configure attached menu if present
                    if hasattr(w, "children") and "menu" in w.children:
                        try:
                            w["menu"].configure(bg=theme["entry_bg"], fg=theme["fg"])
                        except Exception:
                            pass
                except Exception:
                    pass
        except Exception:
            pass

        for child in w.winfo_children():
            _recurse_apply(child)

    _recurse_apply(root)

    # result labels distinct background (ensure readability)
    for res in (result_ltog, result_gtol, conv_frac, conv_decimal, conv_percent, sqrt_result, result_expr, result_numeric):
        try:
            res.configure(bg=theme["result_bg"], fg=theme["fg"])
        except Exception:
            pass

def toggle_theme():
    global is_dark
    is_dark = not is_dark
    apply_theme(dark_theme if is_dark else light_theme)
    theme_button.configure(text="Light Mode" if is_dark else "Dark Mode")

# ---------- UI layout (slim & tall + scrollable content) ----------
root = tk.Tk()
root.title("Number Tools")
# slimmer but taller
root.geometry("480x820")
root.resizable(True, True)

# header with prominent theme switch (stays fixed)
header = tk.Frame(root, padx=12, pady=8)
header.pack(fill="x")
# header bg will be set by apply_theme later
title = tk.Label(header, text="Number Tools", font=("Segoe UI", 16, "bold"))
title.pack(side="left")
widget_groups["labels"].append(title)

theme_button = tk.Button(header, text="Dark Mode", width=12, command=toggle_theme, padx=8, pady=6)
theme_button.pack(side="right")
widget_groups["buttons"].append(theme_button)

# create scrollable area for the rest of the UI
container = tk.Frame(root)
container.pack(fill="both", expand=True)

canvas = tk.Canvas(container, highlightthickness=0)
vscroll = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=vscroll.set)

vscroll.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

scrollable_frame = tk.Frame(canvas)
# put the scrollable_frame into the canvas
canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

def _on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

def _on_canvas_configure(event):
    # expand the inner frame to the canvas width
    canvas.itemconfig(canvas_window, width=event.width)

scrollable_frame.bind("<Configure>", _on_frame_configure)
canvas.bind("<Configure>", _on_canvas_configure)

# mouse wheel scrolling (Windows)
def _on_mousewheel(event):
    # event.delta is multiple of 120 on Windows
    canvas.yview_scroll(-1 * (event.delta // 120), "units")

canvas.bind_all("<MouseWheel>", _on_mousewheel)

# now place the UI inside scrollable_frame (was previously root)
frame_top = tk.Frame(scrollable_frame, padx=12, pady=8)
frame_top.pack(fill="x")
tk.Label(frame_top, text="Enter numbers (decimals, fractions, mixed) separated by commas:").pack(anchor="w")
widget_groups["labels"].append(frame_top.winfo_children()[-1])

#calc
calc_frame = tk.Frame(scrollable_frame, padx=12, pady=8, bd=2, relief="groove")
calc_frame.pack(fill="x", pady=6)

calc_display = tk.Entry(calc_frame, width=28, font=("Segoe UI", 14), justify="right")
calc_display.grid(row=0, column=0, columnspan=4, pady=6)
widget_groups["entries"].append(calc_display)

buttons = [
    ("7",1,0), ("8",1,1), ("9",1,2), ("/",1,3),
    ("4",2,0), ("5",2,1), ("6",2,2), ("*",2,3),
    ("1",3,0), ("2",3,1), ("3",3,2), ("-",3,3),
    ("0",4,0), (".",4,1), ("C",4,2), ("+",4,3),
    ("=",5,0,4)  # span 4 columns
]

for b in buttons:
    text = b[0]
    row, col = b[1], b[2]
    colspan = b[3] if len(b) == 4 else 1
    btn = tk.Button(calc_frame, text=text, width=6, height=2,
                    command=lambda t=text: calc_click(t))
    btn.grid(row=row, column=col, columnspan=colspan, padx=2, pady=2, sticky="nsew")
    widget_groups["buttons"].append(btn)

# Expand buttons evenly
for i in range(4):
    calc_frame.grid_columnconfigure(i, weight=1)


# ---------- Then pack your Number Tools frame ----------
tools_frame = tk.Frame(scrollable_frame, padx=12, pady=8, bd=2, relief="groove")
tools_frame.pack(fill="x", pady=6)

# Expand buttons evenly
for i in range(4):
    calc_frame.grid_columnconfigure(i, weight=1)

entry = tk.Entry(frame_top, width=48)
entry.pack(pady=6)
widget_groups["entries"].append(entry)

btn_sort = tk.Button(frame_top, text="Sort Numbers", command=on_sort, padx=8, pady=4)
btn_sort.pack()
widget_groups["buttons"].append(btn_sort)

tk.Label(frame_top, text="Least → Greatest:").pack(anchor="w", pady=(8,0))
widget_groups["labels"].append(frame_top.winfo_children()[-1])
result_ltog = tk.Label(frame_top, text="", anchor="w", justify="left", wraplength=440, padx=6, pady=4, relief="groove")
result_ltog.pack(fill="x")
widget_groups["labels"].append(result_ltog)

tk.Label(frame_top, text="Greatest → Least:").pack(anchor="w", pady=(8,0))
widget_groups["labels"].append(frame_top.winfo_children()[-1])
result_gtol = tk.Label(frame_top, text="", anchor="w", justify="left", wraplength=440, padx=6, pady=4, relief="groove")
result_gtol.pack(fill="x")
widget_groups["labels"].append(result_gtol)

# converter section
sep = tk.Label(scrollable_frame, text="")
sep.pack(pady=6)
widget_groups["labels"].append(sep)

frame_conv = tk.Frame(scrollable_frame, padx=12, pady=8)
frame_conv.pack(fill="x")
tk.Label(frame_conv, text="Converter (fraction / decimal / percent):").pack(anchor="w")
widget_groups["labels"].append(frame_conv.winfo_children()[-1])

convert_entry = tk.Entry(frame_conv, width=28)
convert_entry.pack(pady=6)
widget_groups["entries"].append(convert_entry)

btn_conv = tk.Button(frame_conv, text="Convert", command=on_convert, padx=8, pady=4)
btn_conv.pack()
widget_groups["buttons"].append(btn_conv)

tk.Label(frame_conv, text="As Fraction:").pack(anchor="w", pady=(8,0))
widget_groups["labels"].append(frame_conv.winfo_children()[-1])
conv_frac = tk.Label(frame_conv, text="", anchor="w", bg=root["bg"])
conv_frac.pack(fill="x")
widget_groups["labels"].append(conv_frac)

tk.Label(frame_conv, text="As Decimal:").pack(anchor="w", pady=(6,0))
widget_groups["labels"].append(frame_conv.winfo_children()[-1])
conv_decimal = tk.Label(frame_conv, text="", anchor="w", bg=root["bg"])
conv_decimal.pack(fill="x")
widget_groups["labels"].append(conv_decimal)

tk.Label(frame_conv, text="As Percent:").pack(anchor="w", pady=(6,0))
widget_groups["labels"].append(frame_conv.winfo_children()[-1])
conv_percent = tk.Label(frame_conv, text="", anchor="w", bg=root["bg"])
conv_percent.pack(fill="x")
widget_groups["labels"].append(conv_percent)

# square root
frame_sqrt = tk.Frame(scrollable_frame, padx=12, pady=8)
frame_sqrt.pack(fill="x")
tk.Label(frame_sqrt, text="Square Root:").pack(anchor="w")
widget_groups["labels"].append(frame_sqrt.winfo_children()[-1])
sqrt_entry = tk.Entry(frame_sqrt, width=22)
sqrt_entry.pack(pady=6)
widget_groups["entries"].append(sqrt_entry)
btn_sqrt = tk.Button(frame_sqrt, text="√", command=on_sqrt, width=8)
btn_sqrt.pack()
widget_groups["buttons"].append(btn_sqrt)
tk.Label(frame_sqrt, text="Result:").pack(anchor="w", pady=(8,0))
widget_groups["labels"].append(frame_sqrt.winfo_children()[-1])
sqrt_result = tk.Label(frame_sqrt, text="", anchor="w")
sqrt_result.pack(fill="x")
widget_groups["labels"].append(sqrt_result)

# exponent rule
frame_exp = tk.Frame(scrollable_frame, padx=12, pady=8)
frame_exp.pack(fill="x")
tk.Label(frame_exp, text="Exponent Rule (symbolic):", font=("Segoe UI", 11, "bold")).pack(anchor="w")
widget_groups["labels"].append(frame_exp.winfo_children()[-1])

tk.Label(frame_exp, text="Base (number or symbol):").pack(anchor="w")
widget_groups["labels"].append(frame_exp.winfo_children()[-1])
base_entry = tk.Entry(frame_exp, width=28)
base_entry.pack(pady=4)
widget_groups["entries"].append(base_entry)

tk.Label(frame_exp, text="Exponent 1:").pack(anchor="w")
widget_groups["labels"].append(frame_exp.winfo_children()[-1])
exp1_entry = tk.Entry(frame_exp, width=14)
exp1_entry.pack(pady=3)
widget_groups["entries"].append(exp1_entry)

tk.Label(frame_exp, text="Exponent 2:").pack(anchor="w")
widget_groups["labels"].append(frame_exp.winfo_children()[-1])
exp2_entry = tk.Entry(frame_exp, width=14)
exp2_entry.pack(pady=3)
widget_groups["entries"].append(exp2_entry)

# friendly short labels -> internal codes
rules_map = {
    "Product Rule": "multiply_same_base",
    "Quotient Rule": "divide_same_base",
    "Power Rule": "power_of_power",
    "Negative Exponent Rule": "negative_exponent",   # <--- added
}
rule_var = tk.StringVar(root)
rule_var.set(next(iter(rules_map.keys())))
option = tk.OptionMenu(frame_exp, rule_var, *rules_map.keys())
option.pack(pady=6)
widget_groups["optionmenus"].append(option)

btn_exp = tk.Button(frame_exp, text="Apply Rule", command=on_exponent_rule, padx=8, pady=4)
btn_exp.pack()
widget_groups["buttons"].append(btn_exp)

# new Evaluate button
btn_eval = tk.Button(frame_exp, text="Evaluate", command=on_exponent_evaluate, padx=8, pady=4)
btn_eval.pack(pady=(4,0))
widget_groups["buttons"].append(btn_eval)

tk.Label(frame_exp, text="Resulting Expression:").pack(anchor="w", pady=(8,0))
widget_groups["labels"].append(frame_exp.winfo_children()[-1])
result_expr = tk.Label(frame_exp, text="", anchor="w", justify="left", wraplength=440, relief="groove", padx=6, pady=4)
result_expr.pack(fill="x")
widget_groups["labels"].append(result_expr)

tk.Label(frame_exp, text="Note: numeric evaluation disabled for exponent rules.").pack(anchor="w", pady=(6,0))
widget_groups["labels"].append(frame_exp.winfo_children()[-1])
result_numeric = tk.Label(frame_exp, text="", anchor="w")
result_numeric.pack(fill="x")
widget_groups["labels"].append(result_numeric)

# Algebraic solver section
alg_frame = tk.Frame(scrollable_frame, padx=12, pady=8)
alg_frame.pack(fill="x")
tk.Label(alg_frame, text="Algebraic Solver (linear in one variable):").pack(anchor="w")
widget_groups["labels"].append(alg_frame.winfo_children()[-1])

tk.Label(alg_frame, text="Enter equation (e.g. 2x+3=7):").pack(anchor="w")
widget_groups["labels"].append(alg_frame.winfo_children()[-1])
alg_entry = tk.Entry(alg_frame, width=36)
alg_entry.pack(pady=6)
widget_groups["entries"].append(alg_entry)

alg_buttons = tk.Frame(alg_frame)
alg_buttons.pack()
btn_alg_solve = tk.Button(alg_buttons, text="Solve", command=on_solve_algebra, padx=8, pady=4)
btn_alg_solve.pack(side="left", padx=6)
widget_groups["buttons"].append(btn_alg_solve)

alg_result_label = tk.Label(alg_frame, text="Result:", anchor="w")
alg_result_label.pack(anchor="w", pady=(8,0))
widget_groups["labels"].append(alg_result_label)
alg_result = tk.Label(alg_frame, text="", anchor="w", justify="left", wraplength=440, relief="groove", padx=6, pady=4)
alg_result.pack(fill="x")
widget_groups["labels"].append(alg_result)

alg_result_dec_label = tk.Label(alg_frame, text="As decimal (if exact):", anchor="w")
alg_result_dec_label.pack(anchor="w", pady=(6,0))
widget_groups["labels"].append(alg_result_dec_label)
alg_result_decimal = tk.Label(alg_frame, text="", anchor="w")
alg_result_decimal.pack(fill="x")
widget_groups["labels"].append(alg_result_decimal)

# ---------- Geometry solver (extended) ----------
def on_geom_update_fields(*_):
    """Update parameter labels based on selected shape (supports up to 3 params).
    Hide unused parameter rows so they disappear from the UI.
    """
    sel = geom_var.get()

    # Ensure all rows are visible by default
    geom_label_p1.grid()
    geom_entry_p1.grid()
    geom_label_p2.grid()
    geom_entry_p2.grid()
    geom_label_p3.grid()
    geom_entry_p3.grid()
    # Clear and enable all entries by default
    geom_entry_p1.configure(state="normal")
    geom_entry_p2.configure(state="normal")
    geom_entry_p3.configure(state="normal")

    # Update labels and hide unused rows per shape
    if sel == "Circle":
        geom_label_p1.config(text="Radius:")
        geom_label_p2.grid_remove(); geom_entry_p2.grid_remove()
        geom_label_p3.grid_remove(); geom_entry_p3.grid_remove()
        geom_entry_p2.delete(0, tk.END); geom_entry_p3.delete(0, tk.END)
    elif sel == "Square":
        geom_label_p1.config(text="Side:")
        geom_label_p2.grid_remove(); geom_entry_p2.grid_remove()
        geom_label_p3.grid_remove(); geom_entry_p3.grid_remove()
        geom_entry_p2.delete(0, tk.END); geom_entry_p3.delete(0, tk.END)
    elif sel == "Rectangle":
        geom_label_p1.config(text="Width:")
        geom_label_p2.config(text="Height:")
        geom_label_p3.grid_remove(); geom_entry_p3.grid_remove()
        geom_entry_p3.delete(0, tk.END)
    elif sel == "Parallelogram":
        geom_label_p1.config(text="Base:")
        geom_label_p2.config(text="Side (for perimeter):")
        geom_label_p3.config(text="Height (for area):")
    elif sel == "Trapezoid":
        geom_label_p1.config(text="Base a:")
        geom_label_p2.config(text="Base b:")
        geom_label_p3.config(text="Height:")
    elif sel == "Triangle Area":
        geom_label_p1.config(text="Base:")
        geom_label_p2.config(text="Height:")
        geom_label_p3.grid_remove(); geom_entry_p3.grid_remove()
        geom_entry_p3.delete(0, tk.END)
    elif sel == "Pythagoras (Hypotenuse)":
        geom_label_p1.config(text="Leg A:")
        geom_label_p2.config(text="Leg B:")
        geom_label_p3.grid_remove(); geom_entry_p3.grid_remove()
        geom_entry_p3.delete(0, tk.END)
    elif sel == "Rhombus":
        geom_label_p1.config(text="Diagonal 1:")
        geom_label_p2.config(text="Diagonal 2:")
        geom_label_p3.grid_remove(); geom_entry_p3.grid_remove()
        geom_entry_p3.delete(0, tk.END)
    elif sel == "Ellipse":
        geom_label_p1.config(text="Semi-major (a):")
        geom_label_p2.config(text="Semi-minor (b):")
        geom_label_p3.grid_remove(); geom_entry_p3.grid_remove()
        geom_entry_p3.delete(0, tk.END)
    else:
        geom_label_p1.config(text="Param 1:")
        geom_label_p2.config(text="Param 2:")
        geom_label_p3.config(text="Param 3:")

def on_compute_geometry():
    sel = geom_var.get()
    p1 = geom_entry_p1.get().strip()
    p2 = geom_entry_p2.get().strip()
    p3 = geom_entry_p3.get().strip()
    try:
        # helper to get float from input (uses parse_number)
        def tof(s):
            return float(parse_number(s))

        if sel == "Circle":
            if not p1:
                messagebox.showwarning("Input Error", "Enter radius.")
                return
            r = tof(p1)
            area = math.pi * r * r
            circ = 2 * math.pi * r
            geom_result.config(text=f"Area = {area:.6g}   Circumference = {circ:.6g}")
        elif sel == "Square":
            if not p1:
                messagebox.showwarning("Input Error", "Enter side length.")
                return
            s = tof(p1)
            geom_result.config(text=f"Area = {s*s:.6g}   Perimeter = {4*s:.6g}")
        elif sel == "Rectangle":
            if not p1 or not p2:
                messagebox.showwarning("Input Error", "Enter width and height.")
                return
            w = tof(p1); h = tof(p2)
            area = w * h
            peri = 2 * (w + h)
            geom_result.config(text=f"Area = {area:.6g}   Perimeter = {peri:.6g}")
        elif sel == "Parallelogram":
            if not p1 or not p3:
                messagebox.showwarning("Input Error", "Enter base and height (side optional for perimeter).")
                return
            base = tof(p1); height = tof(p3)
            area = base * height
            if p2:
                side = tof(p2)
                peri = 2 * (base + side)
                geom_result.config(text=f"Area = {area:.6g}   Perimeter = {peri:.6g}")
            else:
                geom_result.config(text=f"Area = {area:.6g}   Perimeter = (need side length)")
        elif sel == "Trapezoid":
            if not p1 or not p2 or not p3:
                messagebox.showwarning("Input Error", "Enter both bases and height.")
                return
            a = tof(p1); b = tof(p2); h = tof(p3)
            area = 0.5 * (a + b) * h
            geom_result.config(text=f"Area = {area:.6g}   Perimeter = (need leg lengths)")
        elif sel == "Triangle Area":
            if not p1 or not p2:
                messagebox.showwarning("Input Error", "Enter base and height.")
                return
            b = tof(p1); h = tof(p2)
            area = 0.5 * b * h
            geom_result.config(text=f"Area = {area:.6g}")
        elif sel == "Pythagoras (Hypotenuse)":
            if not p1 or not p2:
                messagebox.showwarning("Input Error", "Enter both legs.")
                return
            a = tof(p1); b = tof(p2)
            hyp = math.hypot(a, b)
            geom_result.config(text=f"Hypotenuse = {hyp:.6g}")
        elif sel == "Rhombus":
            if not p1 or not p2:
                messagebox.showwarning("Input Error", "Enter both diagonals.")
                return
            d1 = tof(p1); d2 = tof(p2)
            area = 0.5 * d1 * d2
            # side from half-diagonals
            side = math.hypot(d1/2.0, d2/2.0)
            peri = 4 * side
            geom_result.config(text=f"Area = {area:.6g}   Perimeter = {peri:.6g}")
        elif sel == "Ellipse":
            if not p1 or not p2:
                messagebox.showwarning("Input Error", "Enter semi-major (a) and semi-minor (b).")
                return
            a = tof(p1); b = tof(p2)
            area = math.pi * a * b
            # Ramanujan's approximation for circumference
            h = ((a - b)**2) / ((a + b)**2) if (a + b) != 0 else 0
            circ = math.pi * (a + b) * (1 + (3*h)/(10 + math.sqrt(4 - 3*h)))
            geom_result.config(text=f"Area = {area:.6g}   Circumference ≈ {circ:.6g}")
        else:
            geom_result.config(text="Unknown shape.")
    except ValueError as e:
        messagebox.showerror("Input Error", str(e))
    except Exception as ex:
        messagebox.showerror("Math Error", str(ex))

# ---------- Geometry UI (placed in scrollable_frame) ----------
geom_frame = tk.Frame(scrollable_frame, padx=12, pady=8)
geom_frame.pack(fill="x")
tk.Label(geom_frame, text="Geometry Solver:").pack(anchor="w")
widget_groups["labels"].append(geom_frame.winfo_children()[-1])

tk.Label(geom_frame, text="Shape:").pack(anchor="w")
widget_groups["labels"].append(geom_frame.winfo_children()[-1])
geom_var = tk.StringVar(root)
geom_var.set("Circle")
geom_options = [
    "Circle", "Square", "Rectangle", "Parallelogram",
    "Trapezoid", "Triangle Area", "Pythagoras (Hypotenuse)",
    "Rhombus", "Ellipse"
]
geom_option = tk.OptionMenu(geom_frame, geom_var, *geom_options)
geom_option.pack(pady=4)
widget_groups["optionmenus"].append(geom_option)

param_frame = tk.Frame(geom_frame)
param_frame.pack(fill="x")
geom_label_p1 = tk.Label(param_frame, text="Param 1:")
geom_label_p1.grid(row=0, column=0, sticky="w")
geom_entry_p1 = tk.Entry(param_frame, width=18)
geom_entry_p1.grid(row=0, column=1, padx=6, pady=4)
widget_groups["labels"].append(geom_label_p1); widget_groups["entries"].append(geom_entry_p1)

geom_label_p2 = tk.Label(param_frame, text="Param 2:")
geom_label_p2.grid(row=1, column=0, sticky="w")
geom_entry_p2 = tk.Entry(param_frame, width=18)
geom_entry_p2.grid(row=1, column=1, padx=6, pady=4)
widget_groups["labels"].append(geom_label_p2); widget_groups["entries"].append(geom_entry_p2)

geom_label_p3 = tk.Label(param_frame, text="Param 3:")
geom_label_p3.grid(row=2, column=0, sticky="w")
geom_entry_p3 = tk.Entry(param_frame, width=18)
geom_entry_p3.grid(row=2, column=1, padx=6, pady=4)
widget_groups["labels"].append(geom_label_p3); widget_groups["entries"].append(geom_entry_p3)

# compute button and result
btn_geom = tk.Button(geom_frame, text="Compute", command=on_compute_geometry, padx=8, pady=4)
btn_geom.pack(pady=(4,0))
widget_groups["buttons"].append(btn_geom)

tk.Label(geom_frame, text="Result:").pack(anchor="w", pady=(8,0))
widget_groups["labels"].append(geom_frame.winfo_children()[-1])
geom_result = tk.Label(geom_frame, text="", anchor="w", justify="left", wraplength=440, relief="groove", padx=6, pady=4)
geom_result.pack(fill="x")
widget_groups["labels"].append(geom_result)

# hook update when shape changes
geom_var.trace_add("write", on_geom_update_fields)
on_geom_update_fields()

# ensure geometry widgets are included in theme groups
widget_groups["optionmenus"].append(geom_option)
widget_groups["buttons"].append(btn_geom)

# apply initial theme and start UI
frame_stats = tk.Frame(scrollable_frame, padx=12, pady=8)
frame_stats.pack(fill="x")

tk.Label(frame_stats, text="Mean, Median, Range:", font=("Segoe UI", 11, "bold")).pack(anchor="w")
widget_groups["labels"].append(frame_stats.winfo_children()[-1])

stats_entry = tk.Entry(frame_stats, width=48)
stats_entry.pack(pady=6)
widget_groups["entries"].append(stats_entry)

stats_result = tk.Label(frame_stats, text="", anchor="w", justify="left", wraplength=440, relief="groove", padx=6, pady=4)
stats_result.pack(fill="x")
widget_groups["labels"].append(stats_result)

def on_calculate_stats():
    s = stats_entry.get()
    if not s.strip():
        messagebox.showwarning("Input Error", "Enter numbers separated by commas.")
        return
    numbers = s.split(',')
    try:
        mean_val, median_val, range_val = calculate_stats(numbers)
        stats_result.config(
            text=f"Mean: {fraction_to_decimal_str(mean_val)}\n"
                 f"Median: {fraction_to_decimal_str(median_val)}\n"
                 f"Range: {fraction_to_decimal_str(range_val)}"
        )
    except ValueError as e:
        messagebox.showerror("Input Error", str(e))

btn_stats = tk.Button(frame_stats, text="Calculate Stats", command=on_calculate_stats, padx=8, pady=4)
btn_stats.pack()
widget_groups["buttons"].append(btn_stats)

apply_theme(light_theme)
root.mainloop()
