"""
NetTracer - Native Vector Icon Engine
Draws sleek, monochrome vector icons via QPainter without relying on system emoji fonts.
"""

from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPixmap, QPainterPath


class VectorIcons:
    """Provides crisp, scalable monochrome vector icons."""

    @staticmethod
    def render_pixmap(icon_name: str, size: int = 24, color: str = "#9ca3af", fill: bool = False) -> QPixmap:
        pix = QPixmap(size, size)
        pix.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        c = QColor(color)
        pen_width = max(1.5, size / 12.0)
        pen = QPen(c, pen_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)

        if fill:
            painter.setBrush(QBrush(c))
        else:
            painter.setBrush(Qt.BrushStyle.NoBrush)

        s = float(size)
        pad = s * 0.15
        rect = QRectF(pad, pad, s - 2 * pad, s - 2 * pad)

        name = icon_name.lower().replace("-", "_")

        if name in ("dashboard", "squares_four", "grid"):
            # 4 rounded squares (2x2 grid)
            gap = s * 0.08
            sq = (rect.width() - gap) / 2.0
            r = sq * 0.25
            for row in range(2):
                for col in range(2):
                    x = rect.left() + col * (sq + gap)
                    y = rect.top() + row * (sq + gap)
                    if fill:
                        painter.drawRoundedRect(QRectF(x, y, sq, sq), r, r)
                    else:
                        painter.drawRoundedRect(QRectF(x, y, sq, sq), r, r)

        elif name in ("charts", "chart_line", "analytics"):
            # Trend line rising with arrow
            path = QPainterPath()
            path.moveTo(rect.left(), rect.bottom() - rect.height() * 0.2)
            path.lineTo(rect.left() + rect.width() * 0.35, rect.bottom() - rect.height() * 0.55)
            path.lineTo(rect.left() + rect.width() * 0.65, rect.bottom() - rect.height() * 0.35)
            path.lineTo(rect.right(), rect.top() + rect.height() * 0.15)
            painter.drawPath(path)
            # Arrowhead at end
            arr = QPainterPath()
            arr.moveTo(rect.right() - s * 0.15, rect.top() + rect.height() * 0.15)
            arr.lineTo(rect.right(), rect.top() + rect.height() * 0.15)
            arr.lineTo(rect.right(), rect.top() + rect.height() * 0.3)
            painter.drawPath(arr)

        elif name in ("history", "clock"):
            # Clock circle with hands
            painter.drawEllipse(rect)
            center = rect.center()
            path = QPainterPath()
            path.moveTo(center.x(), center.y())
            path.lineTo(center.x(), rect.top() + rect.height() * 0.25)  # Minute hand
            path.moveTo(center.x(), center.y())
            path.lineTo(rect.right() - rect.width() * 0.28, center.y())  # Hour hand
            painter.drawPath(path)

        elif name in ("security", "shield"):
            # Shield with checkmark
            cx = rect.center().x()
            path = QPainterPath()
            path.moveTo(cx, rect.top())
            path.lineTo(rect.right(), rect.top() + rect.height() * 0.2)
            path.quadTo(rect.right(), rect.bottom() * 0.85, cx, rect.bottom())
            path.quadTo(rect.left(), rect.bottom() * 0.85, rect.left(), rect.top() + rect.height() * 0.2)
            path.closeSubpath()
            painter.drawPath(path)
            # Checkmark inside
            chk = QPainterPath()
            chk.moveTo(cx - s * 0.12, rect.top() + rect.height() * 0.5)
            chk.lineTo(cx - s * 0.02, rect.top() + rect.height() * 0.62)
            chk.lineTo(cx + s * 0.14, rect.top() + rect.height() * 0.38)
            painter.drawPath(chk)

        elif name in ("settings", "gear"):
            # Minimalist gear/cog
            cx = rect.center().x()
            cy = rect.center().y()
            r_outer = rect.width() * 0.46
            r_inner = rect.width() * 0.22
            # Center circle
            painter.drawEllipse(rect.center(), r_inner, r_inner)
            # Teeth / outer ring
            painter.drawEllipse(rect.center(), r_outer, r_outer)
            for i in range(6):
                angle_deg = i * 60
                rad = angle_deg * 3.14159 / 180.0
                x1 = cx + (r_outer - 1) * 3.14159 / 3.14159 * 0 + cx  # dummy
                p1 = QPointF(cx + (r_outer - 1) * (1 if i == 0 else 0), cy)
                painter.drawLine(
                    QPointF(cx + (r_outer - 2) * (Qt.AlignmentFlag.AlignCenter if False else 1) * (0.9 * c.red() / 255.0 * 0 + (1 if i == 0 else 0)), cy),
                    QPointF(cx, cy)
                )

        elif name in ("chrome", "browser", "globe"):
            # Globe
            painter.drawEllipse(rect)
            painter.drawLine(QPointF(rect.left(), rect.center().y()), QPointF(rect.right(), rect.center().y()))
            painter.drawEllipse(rect.center(), rect.width() * 0.28, rect.height() * 0.5)

        elif name in ("telegram", "paper_plane"):
            # Paper airplane
            path = QPainterPath()
            path.moveTo(rect.left(), rect.center().y())
            path.lineTo(rect.right(), rect.top())
            path.lineTo(rect.center().x() + s * 0.1, rect.bottom())
            path.lineTo(rect.center().x(), rect.center().y() + s * 0.1)
            path.closeSubpath()
            painter.drawPath(path)

        elif name in ("spotify", "music"):
            # Music note
            cx = rect.center().x()
            path = QPainterPath()
            path.moveTo(cx + s * 0.1, rect.top() + s * 0.1)
            path.lineTo(cx + s * 0.1, rect.bottom() - s * 0.15)
            painter.drawPath(path)
            painter.setBrush(QBrush(c))
            painter.drawEllipse(QRectF(cx - s * 0.15, rect.bottom() - s * 0.25, s * 0.26, s * 0.2))

        elif name in ("pacman", "package"):
            # Package cube box
            cx = rect.center().x()
            cy = rect.center().y()
            path = QPainterPath()
            path.moveTo(cx, rect.top())
            path.lineTo(rect.right(), rect.top() + rect.height() * 0.25)
            path.lineTo(rect.right(), rect.bottom() - rect.height() * 0.25)
            path.lineTo(cx, rect.bottom())
            path.lineTo(rect.left(), rect.bottom() - rect.height() * 0.25)
            path.lineTo(rect.left(), rect.top() + rect.height() * 0.25)
            path.closeSubpath()
            path.moveTo(cx, rect.top())
            path.lineTo(cx, cy)
            path.lineTo(rect.right(), rect.top() + rect.height() * 0.25)
            path.moveTo(cx, cy)
            path.lineTo(rect.left(), rect.top() + rect.height() * 0.25)
            painter.drawPath(path)

        elif name in ("firefox",):
            # Clean browser icon
            painter.drawRoundedRect(rect, 4, 4)
            painter.drawLine(QPointF(rect.left(), rect.top() + s * 0.2), QPointF(rect.right(), rect.top() + s * 0.2))

        elif name in ("docker", "container"):
            # Server / container box
            painter.drawRoundedRect(rect, 3, 3)
            painter.drawLine(QPointF(rect.left(), rect.center().y()), QPointF(rect.right(), rect.center().y()))

        elif name in ("suspend", "pause"):
            # Two vertical pause bars
            bar_w = s * 0.12
            h = rect.height() * 0.8
            y = rect.top() + rect.height() * 0.1
            painter.setBrush(QBrush(c))
            painter.drawRoundedRect(QRectF(rect.center().x() - bar_w * 1.5, y, bar_w, h), bar_w / 2, bar_w / 2)
            painter.drawRoundedRect(QRectF(rect.center().x() + bar_w * 0.5, y, bar_w, h), bar_w / 2, bar_w / 2)

        elif name in ("resume", "play"):
            # Play triangle
            path = QPainterPath()
            path.moveTo(rect.left() + s * 0.1, rect.top() + s * 0.05)
            path.lineTo(rect.right() - s * 0.05, rect.center().y())
            path.lineTo(rect.left() + s * 0.1, rect.bottom() - s * 0.05)
            path.closeSubpath()
            painter.setBrush(QBrush(c))
            painter.drawPath(path)

        elif name in ("export",):
            # Tray + arrow
            path = QPainterPath()
            # Tray
            path.moveTo(rect.left(), rect.center().y())
            path.lineTo(rect.left(), rect.bottom())
            path.lineTo(rect.right(), rect.bottom())
            path.lineTo(rect.right(), rect.center().y())
            # Arrow up
            cx = rect.center().x()
            path.moveTo(cx, rect.bottom() - s * 0.15)
            path.lineTo(cx, rect.top())
            path.moveTo(cx - s * 0.15, rect.top() + s * 0.15)
            path.lineTo(cx, rect.top())
            path.lineTo(cx + s * 0.15, rect.top() + s * 0.15)
            painter.drawPath(path)

        elif name in ("download", "arrow_down"):
            # Arrow pointing down-left
            path = QPainterPath()
            path.moveTo(rect.right(), rect.top())
            path.lineTo(rect.left(), rect.bottom())
            path.moveTo(rect.left() + s * 0.25, rect.bottom())
            path.lineTo(rect.left(), rect.bottom())
            path.lineTo(rect.left(), rect.bottom() - s * 0.25)
            painter.drawPath(path)

        elif name in ("upload", "arrow_up"):
            # Arrow pointing up-right
            path = QPainterPath()
            path.moveTo(rect.left(), rect.bottom())
            path.lineTo(rect.right(), rect.top())
            path.moveTo(rect.right() - s * 0.25, rect.top())
            path.lineTo(rect.right(), rect.top())
            path.lineTo(rect.right(), rect.top() + s * 0.25)
            painter.drawPath(path)

        elif name in ("live", "broadcast"):
            # Radio broadcast waves ((•))
            cx = rect.center().x()
            cy = rect.center().y()
            painter.setBrush(QBrush(c))
            painter.drawEllipse(QPointF(cx, cy), s * 0.06, s * 0.06)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawArc(QRectF(cx - s * 0.2, cy - s * 0.2, s * 0.4, s * 0.4), int(120 * 16), int(120 * 16))
            painter.drawArc(QRectF(cx - s * 0.2, cy - s * 0.2, s * 0.4, s * 0.4), int(-60 * 16), int(120 * 16))
            painter.drawArc(QRectF(cx - s * 0.34, cy - s * 0.34, s * 0.68, s * 0.68), int(130 * 16), int(100 * 16))
            painter.drawArc(QRectF(cx - s * 0.34, cy - s * 0.34, s * 0.68, s * 0.68), int(-50 * 16), int(100 * 16))

        elif name in ("presentation_chart", "analytics_board"):
            # Clean presentation easel / chart board
            board = QRectF(rect.left(), rect.top(), rect.width(), rect.height() * 0.7)
            painter.drawRoundedRect(board, 3, 3)
            # 3 bars inside board
            bar_w = board.width() * 0.16
            gap = board.width() * 0.1
            b_bot = board.bottom() - board.height() * 0.15
            b_top1 = b_bot - board.height() * 0.35
            b_top2 = b_bot - board.height() * 0.65
            b_top3 = b_bot - board.height() * 0.45
            x0 = board.left() + board.width() * 0.18
            painter.setBrush(QBrush(c))
            painter.drawRect(QRectF(x0, b_top1, bar_w, b_bot - b_top1))
            painter.drawRect(QRectF(x0 + bar_w + gap, b_top2, bar_w, b_bot - b_top2))
            painter.drawRect(QRectF(x0 + (bar_w + gap) * 2, b_top3, bar_w, b_bot - b_top3))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            # Easel stand legs
            cx = board.center().x()
            painter.drawLine(QPointF(cx, board.bottom()), QPointF(rect.left() + s * 0.1, rect.bottom()))
            painter.drawLine(QPointF(cx, board.bottom()), QPointF(rect.right() - s * 0.1, rect.bottom()))

        else:
            # Fallback neat circle
            painter.drawEllipse(rect)

        painter.end()
        return pix
