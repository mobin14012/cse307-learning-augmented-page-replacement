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
        ("Abstract", "This paper evaluates FIFO, LRU, Belady's optimal replacement, and a lightweight decision-tree eviction heuristic on three independently seeded synthetic traces. Each trace changes at its midpoint from locality-heavy references to broad random access. We report means and sample standard deviations, examining how working-set changes affect faults and whether simple history features respond to the shift. Optimal provides an offline lower bound, not an implementable online policy."),
        ("1. Problem framing", "Virtual memory allows a process to use a logical address space larger than physical memory, but a reference to a non-resident page causes a page fault. When a frame is full, the replacement policy chooses a victim. FIFO is simple but ignores reuse, while LRU uses the recent past as a proxy for near-future reuse. Belady's optimal policy chooses the page whose next use is farthest away and is useful as an offline comparison [1,2]. The course brief asks whether a lightweight learned layer can respond when the workload changes [4]."),
        ("2. Implementation and learned component", "The Python program implements all four policies. The learned policy uses a depth-4 decision tree. For each resident candidate, its features are age since last reference, frequency in the previous 64 references, and whether it was touched in the previous eight references. Training uses an independent seeded trace. Labels identify the candidate with the farthest next use in a 96-reference horizon. During evaluation, only current/history features are supplied. This is an interpretable heuristic, but the labels use future information during training, so it is not a fully online production predictor [3]."),
        ("3. Experimental setup", "Three evaluation traces use seeds 307, 308, and 309. Each contains 1,000 references. References 0–499 are locality-heavy: 82% of accesses select from a small hot set, with occasional sequential accesses. At reference 500, the distribution shifts to uniform random references over 32 pages. Each policy is tested with 4, 8, and 12 frames; the main comparison uses 8 frames. Each trace is replayed unchanged for all policies. The learned tree is trained once on an independent trace and held fixed. Per-seed traces and measurements are stored in results/."),
    ]
    for heading, text in sections:
        story += [p(heading, styles["Heading2"]), p(text, styles["BodyText"]), Spacer(1, 5)]
    story += [p("4. Results and analysis", styles["Heading2"]), p("Table 1 reports the mean and sample standard deviation of page faults across three runs (500 accesses per phase). Optimal has the fewest faults because it sees the future. LRU performs better than FIFO in the locality phase, where reuse helps recency. Following the shift, every policy incurs substantially more faults as the request distribution broadens beyond the small hot set. The learned heuristic has the lowest locality-phase mean among the implementable policies, but its shifted-phase hit ratio is lower than those of FIFO and LRU. The fixed model's training labels and feature patterns do not generalize equally well to the shifted distribution, illustrating that learned heuristics can be sensitive to distribution mismatch.", styles["BodyText"]), Spacer(1, 5)]
    data = [["Policy", "Local faults\nmean ± SD", "Local hit", "Shift faults\nmean ± SD", "Shift hit"], ["FIFO", "138.3 ± 8.1", "0.723", "375.0 ± 9.6", "0.250"], ["LRU", "110.0 ± 6.6", "0.780", "372.7 ± 16.2", "0.255"], ["Optimal", "57.3 ± 1.5", "0.885", "231.7 ± 5.9", "0.537"], ["Learned", "79.0 ± 2.6", "0.842", "383.7 ± 11.6", "0.233"]]
    table = Table(data, colWidths=[.9*inch, 1.25*inch, .82*inch, 1.3*inch, .8*inch], hAlign="CENTER")
    table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.lightgrey), ("GRID", (0,0), (-1,-1), .5, colors.grey), ("ALIGN", (1,1), (-1,-1), "CENTER"), ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold")]))
    story += [p("Table 1. Eight-frame results from the seeded run.", styles["Small"]), table, Spacer(1, 8), Image(str(ROOT / "results" / "page_faults.png"), width=6.6*inch, height=2.77*inch), p("Figure 1. Fault counts before and after the distribution shift for eight frames.", styles["Small"])]
    story += [p("5. Conclusion", styles["Heading2"]), p("Across the three generated seeds, the broad random phase consistently produces many more faults than the locality phase. The learned policy is strongest during locality for the tested 8-frame setup but does not retain that advantage after the workload shift. These synthetic results illustrate a limitation of using a fixed learned decision rule across changing distributions. Additional seeds, online labels, and real traces would be needed before making claims about deployment.", styles["BodyText"]), p("References", styles["Heading2"]), p("[1] L. A. Belady, ‘A study of replacement algorithms for a virtual-storage computer,’ IBM Systems Journal, 1966.<br/>[2] R. L. Mattson et al., ‘Evaluation techniques for storage hierarchies,’ IBM Systems Journal, 1970.<br/>[3] scikit-learn developers, DecisionTreeClassifier documentation, 2025.<br/>[4] CSE-307 course staff, Term Paper Brief — Section B, 2026.", styles["Small"])]
    doc.build(story)
    print(f"Built {OUT}")


if __name__ == "__main__":
    main()
