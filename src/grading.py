#!/usr/bin/env python3
"""
Letter grade conversion for school health scores
Makes scores more intuitive and actionable
"""

def get_letter_grade(score):
    """
    Convert numeric health score (0-100) to letter grade (A-F)
    Lower scores = better (less health need)
    
    Grade Scale:
    A (Excellent):        0-25  - Minimal health needs, strong support systems
    B (Good):            25-35  - Low health needs, adequate support
    C (Fair):            35-45  - Moderate needs, attention required
    D (Needs Action):    45-55  - High needs, urgent action required
    F (Critical):        55+    - Critical needs, immediate intervention
    """
    if score < 25:
        return 'A', 'Excellent', 'success'
    elif score < 35:
        return 'B', 'Good', 'success'
    elif score < 45:
        return 'C', 'Fair', 'warning'
    elif score < 55:
        return 'D', 'Needs Action', 'danger'
    else:
        return 'F', 'Critical', 'danger'

def get_grade_explanation():
    """
    Return HTML explanation of grading scale
    """
    return """
    <div class="grade-legend">
        <h4>Understanding Health Grades</h4>
        <div class="grade-scale">
            <div class="grade-item grade-a">
                <div class="grade-letter">A</div>
                <div class="grade-info">
                    <div class="grade-label">Excellent</div>
                    <div class="grade-desc">Minimal health needs. Strong community health and adequate medical support.</div>
                </div>
            </div>
            <div class="grade-item grade-b">
                <div class="grade-letter">B</div>
                <div class="grade-info">
                    <div class="grade-label">Good</div>
                    <div class="grade-desc">Low health needs. Standard wellness programs are sufficient.</div>
                </div>
            </div>
            <div class="grade-item grade-c">
                <div class="grade-letter">C</div>
                <div class="grade-info">
                    <div class="grade-label">Fair</div>
                    <div class="grade-desc">Moderate needs. Enhanced health services and monitoring recommended.</div>
                </div>
            </div>
            <div class="grade-item grade-d">
                <div class="grade-letter">D</div>
                <div class="grade-info">
                    <div class="grade-label">Needs Action</div>
                    <div class="grade-desc">High needs. Urgent placement of full-time nurse and wellness programs required.</div>
                </div>
            </div>
            <div class="grade-item grade-f">
                <div class="grade-letter">F</div>
                <div class="grade-info">
                    <div class="grade-label">Critical</div>
                    <div class="grade-desc">Critical needs. Immediate intervention required. Multiple health support gaps.</div>
                </div>
            </div>
        </div>
        <p class="grade-note">Grades reflect combined health burden (chronic disease, doctor availability, environmental factors) and available support (nurse staffing).</p>
    </div>
    """

def get_grade_styles():
    """
    Return CSS for grade display
    """
    return """
    .grade-display{font-size:3rem;font-weight:700;line-height:1;font-family:Georgia,serif}
    .grade-display.grade-a,.grade-display.grade-b{color:#2e7d32}
    .grade-display.grade-c{color:#f57c00}
    .grade-display.grade-d,.grade-display.grade-f{color:#d32f2f}
    .grade-label-text{font-size:0.7rem;color:#888;text-transform:uppercase;margin-top:4px}
    .numeric-score{font-size:0.75rem;color:#999;margin-top:2px}
    .grade-legend{background:#f9f9f9;border:1px solid #e0e0e0;border-radius:8px;padding:20px;margin:24px 0}
    .grade-legend h4{margin:0 0 16px 0;font-size:1.1rem;color:#1a1a1a}
    .grade-scale{display:grid;gap:12px}
    .grade-item{display:flex;gap:16px;align-items:center;padding:12px;background:white;border-radius:6px}
    .grade-letter{font-size:2rem;font-weight:700;font-family:Georgia,serif;min-width:50px;text-align:center}
    .grade-item.grade-a .grade-letter,.grade-item.grade-b .grade-letter{color:#2e7d32}
    .grade-item.grade-c .grade-letter{color:#f57c00}
    .grade-item.grade-d .grade-letter,.grade-item.grade-f .grade-letter{color:#d32f2f}
    .grade-info{flex:1}
    .grade-label{font-weight:600;font-size:0.95rem;margin-bottom:4px}
    .grade-desc{font-size:0.85rem;color:#666;line-height:1.4}
    .grade-note{font-size:0.85rem;color:#666;margin-top:16px;font-style:italic}
    @media (min-width:768px){
    .grade-legend{padding:24px}
    .grade-scale{grid-template-columns:repeat(2,1fr)}
    .grade-item.grade-f{grid-column:1/-1}
    }
    """

if __name__ == "__main__":
    # Test grading
    test_scores = [15, 28, 40, 50, 58]
    print("=== GRADE CONVERSION TEST ===")
    for score in test_scores:
        letter, label, color = get_letter_grade(score)
        print(f"Score {score:.1f} → Grade {letter} ({label}) [{color}]")

