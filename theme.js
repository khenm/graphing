const GraphTheme = {
    canvas: {
        background: "#f0f2f5",
    },
    nodes: {
        defaultColor: "#94a3b8",
        // Node fill color keyed by Status property (lowercase)
        statusColors: {
            "learning":     "#bfdbfe",  // pastel blue
            "reviewed":     "#bbf7d0",  // pastel green
            "not started":  "#fecaca",  // pastel red
            "mastered":     "#fef08a"   // pastel yellow
        },
        masteredStarColor: "#92400e", 
        tagColors: {
            "Linear Algebra":       "#60a5fa",
            "Information Theory":   "#a78bfa",
            "Optimization":         "#f472b6",
            "Practice":             "#34d399"
        },
        radius: 8,
        textColor: "#1e293b",
        textOffset: 10,
        hoverOutline: "#475569",
        hoverOutlineWidth: 2
    },
    links: {
        color: "#94a3b8",
        hoverColor: "#475569",
        arrowLength: 6,
        width: 1.5
    },
    ui: {
        buttonBackground: "#e2e8f0",
        buttonText: "#374151",
        buttonBorder: "#94a3b8",
        buttonHoverBackground: "#cbd5e1"
    }
};
