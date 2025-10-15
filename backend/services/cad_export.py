"""
Minimal CAD exporter for prototype:
- DXF: 2D outlines (hour lines / azimuth lines)
- STL: simple prism (gnomon) or pillar shell mesh
- GLTF: small placeholder scene with metadata
- PDF: one-page dimension sheet
(Real pipeline can expand later.)
"""
from io import BytesIO
from typing import Any
import math

import ezdxf
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from pygltflib import GLTF2, Scene, Node, Asset
import trimesh
import numpy as np

class CADExporter:
    def export(self, generator: Any, format: str) -> bytes:
        fmt = format.lower()
        if fmt == "dxf":
            return self.export_dxf(generator)
        if fmt == "stl":
            return self.export_stl(generator)
        if fmt == "gltf":
            return self.export_gltf(generator)
        if fmt == "pdf":
            return self.export_pdf(generator)
        # STEP/SVG can be added later; return PDF fallback
        return self.export_pdf(generator)

    # ---------- DXF ----------
    def export_dxf(self, generator: Any) -> bytes:
        doc = ezdxf.new("R2010")
        msp = doc.modelspace()

        # Try Samrat hour lines; fall back to Rama azimuth lines
        lines_added = 0
        if hasattr(generator, "get_hour_line_coordinates"):
            for seg in generator.get_hour_line_coordinates():
                (x1, y1, z1) = seg["start"]
                (x2, y2, z2) = seg["end"]
                msp.add_line((x1, y1), (x2, y2))
                lines_added += 1
        elif hasattr(generator, "get_azimuth_markings"):
            for seg in generator.get_azimuth_markings():
                (x1, y1, z1) = seg["start"]
                (x2, y2, z2) = seg["end"]
                msp.add_line((x1, y1), (x2, y2))
                lines_added += 1

        if lines_added == 0:
            # draw a small cross so file isn't empty
            msp.add_line((-1, 0), (1, 0))
            msp.add_line((0, -1), (0, 1))

        buf = BytesIO()
        doc.write(buf)
        return buf.getvalue()

    # ---------- STL ----------
    def export_stl(self, generator: Any) -> bytes:
        # Build a very simple mesh: if Samrat, extrude the gnomon triangle; if Rama, a cylinder slice.
        try:
            if hasattr(generator, "get_gnomon_vertices"):
                V = generator.get_gnomon_vertices().astype(np.float64)
                # Create a convex hull for a watertight STL
                mesh = trimesh.Trimesh(vertices=V, faces=trimesh.convex.convex_hull(V).faces)
            elif hasattr(generator, "geometry") and hasattr(generator.geometry, "pillar_radius"):
                g = generator.geometry
                theta = np.linspace(0, math.pi, 48)  # semicircle
                r = g.pillar_radius
                z0, z1 = 0.0, g.pillar_height
                ring0 = np.c_[r*np.cos(theta), r*np.sin(theta), np.full_like(theta, z0)]
                ring1 = np.c_[r*np.cos(theta), r*np.sin(theta), np.full_like(theta, z1)]
                V = np.vstack([ring0, ring1])
                F = []
                n = len(theta)
                for i in range(n-1):
                    # quad into two triangles
                    F.append([i, i+1, i+n])
                    F.append([i+1, i+n+1, i+n])
                mesh = trimesh.Trimesh(vertices=V, faces=np.array(F))
            else:
                mesh = trimesh.creation.box(extents=(1, 0.2, 0.5))
        except Exception:
            mesh = trimesh.creation.box(extents=(1, 0.2, 0.5))

        return mesh.export(file_type="stl")

    # ---------- GLTF ----------
    def export_gltf(self, generator: Any) -> bytes:
        # Minimal GLTF skeleton with an empty scene; good enough for a placeholder preview
        gltf = GLTF2(
            scenes=[Scene(nodes=[0])],
            nodes=[Node(name="YantraRoot")],
            asset=Asset(version="2.0", generator="YantraExporter")
        )
        buf = BytesIO()
        gltf.save_to_bytesio(buf)
        return buf.getvalue()

    # ---------- PDF ----------
    def export_pdf(self, generator: Any) -> bytes:
        buf = BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        W, H = A4

        c.setFont("Helvetica-Bold", 16)
        c.drawString(40, H-60, "Parametric Yantra – Dimension Sheet (Prototype)")

        c.setFont("Helvetica", 10)
        if hasattr(generator, "get_dimensions_dict"):
            dims = generator.get_dimensions_dict()
            y = H-90
            for k, v in dims.items():
                if isinstance(v, dict):
                    c.drawString(40, y, f"{k}:")
                    y -= 14
                    for k2, v2 in v.items():
                        c.drawString(60, y, f"- {k2}: {v2}")
                        y -= 12
                        if y < 80:
                            c.showPage(); y = H-60
                else:
                    c.drawString(40, y, f"{k}: {v}")
                    y -= 12
                    if y < 80:
                        c.showPage(); y = H-60
        else:
            c.drawString(40, H-90, "No dimension details available in generator.")

        c.showPage()
        c.save()
        return buf.getvalue()
