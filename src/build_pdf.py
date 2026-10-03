"""Build a submission-ready PDF without requiring a TeX installation."""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "report" / "term-paper.pdf"


def p(text, style):
    return Paragraph(text, style)


def main():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleCenter", parent=styles["Title"], alignment=TA_CENTER, fontSize=16, leading=20))
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8.5, leading=11))
    doc = SimpleDocTemplate(str(OUT), pagesize=A4, rightMargin=.65*inch, leftMargin=.65*inch, topMargin=.55*inch, bottomMargin=.55*inch)
    story = [p("Learning-Augmented Page Replacement Under a Workload Shift", styles["TitleCenter"]), p("Student Name — Student ID<br/>CSE-307 Operating Systems — Section B", styles["Normal"]), Spacer(1, 8)]
    sections = [
        ("Abstract", "This paper evaluates FIFO, LRU, Belady's optimal replacement, and a lightweight decision-tree eviction heuristic on a seeded synthetic trace. The trace begins with locality-heavy references and changes at its midpoint to broad random access. The experiment shows how increasing the working set changes fault behavior and tests whether simple history features can adapt to the shift. The optimal policy provides an offline lower bound; it is not an implementable online policy."),
        ("1. Problem framing", "Virtual memory allows a process to use a logical address space larger than physical memory, but a reference to a non-resident page causes a page fault. When a frame is full, the replacement policy chooses a victim. FIFO is simple but ignores reuse, while LRU uses the recent past as a proxy for near-future reuse. Belady's optimal policy chooses the page whose next use is farthest away and is useful as an offline comparison [1,2]. The course brief asks whether a lightweight learned layer can respond when the workload changes [4]."),
        ("2. Implementation and learned component", "The Python program implements all four policies. The learned policy uses a depth-4 decision tree. For each resident candidate, its features are age since last reference, frequency in the previous 64 references, and whether it was touched in the previous eight references. Training uses an independent seeded trace. Labels identify the candidate with the farthest next use in a 96-reference horizon. During evaluation, only current/history features are supplied. This is an interpretable heuristic, but the labels use future information during training, so it is not a fully online production predictor [3]."),
        ("3. Experimental setup", "The evaluation trace contains 1,000 references and uses random seed 307. References 0–499 are locality-heavy: 82% of accesses select from a small hot set, with occasional sequential accesses. At reference 500, the distribution shifts to uniform random references over 32 pages. Each policy is tested with 4, 8, and 12 frames; the main comparison uses 8 frames. The same trace is replayed for every policy. The exact trace and metadata are stored in results/."),
    ]
    for heading, text in sections:
        story += [p(heading, styles["Heading2"]), p(text, styles["BodyText"]), Spacer(1, 5)]
    story += [p("4. Results and analysis", styles["Heading2"]), p("Table 1 reports the 8-frame results generated from results/metrics.csv. Optimal has the fewest faults because it sees the future. LRU benefits from repeated hot-page references in the first phase, while FIFO can evict a frequently reused page simply because it arrived earlier. After the shift, the larger effective working set reduces all hit ratios. The learned policy performs well during locality, but its history features and training distribution do not generalize as well to the random phase; this illustrates that learning can adapt to patterns but can also amplify distribution mismatch.", styles["BodyText"]), Spacer(1, 5)]
    data = [["Policy", "Local faults", "Local hit", "Shift faults", "Shift hit"], ["FIFO", "129", "0.742", "379", "0.242"], ["LRU", "109", "0.782", "382", "0.236"], ["Optimal", "56", "0.888", "234", "0.532"], ["Learned", "81", "0.838", "396", "0.208"]]
    table = Table(data, colWidths=[1.2*inch, 1.1*inch, 1.0*inch, 1.1*inch, 1.0*inch], hAlign="CENTER")
    table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.lightgrey), ("GRID", (0,0), (-1,-1), .5, colors.grey), ("ALIGN", (1,1), (-1,-1), "CENTER"), ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold")]))
    story += [p("Table 1. Eight-frame results from the seeded run.", styles["Small"]), table, Spacer(1, 8), Image(str(ROOT / "results" / "page_faults.png"), width=6.6*inch, height=2.77*inch), p("Figure 1. Fault counts before and after the distribution shift for eight frames.", styles["Small"])]
    story += [p("5. Conclusion", styles["Heading2"]), p("The experiment connects classical memory-management policies to a small adaptive component without changing the workload between policies. The shift demonstrates why a policy tuned to stable locality may degrade when the working set broadens. Future work should use multiple seeds, online labels, confidence calibration, and real traces before making deployment claims.", styles["BodyText"]), p("References", styles["Heading2"]), p("[1] L. A. Belady, ‘A study of replacement algorithms for a virtual-storage computer,’ IBM Systems Journal, 1966.<br/>[2] R. L. Mattson et al., ‘Evaluation techniques for storage hierarchies,’ IBM Systems Journal, 1970.<br/>[3] scikit-learn developers, DecisionTreeClassifier documentation, 2025.<br/>[4] CSE-307 course staff, Term Paper Brief — Section B, 2026.", styles["Small"])]
    doc.build(story)
    print(f"Built {OUT}")


if __name__ == "__main__":
    main()
