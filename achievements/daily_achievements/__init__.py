"""
Registry of the FULL pool of possible daily achievements. Which ones
are actually active on a given day is decided by daily.py, not here -
this is just every achievement eligible to be picked.
"""

from .._base import DailyAchievement

# General
from .do_operations import DoOperations
from .select_objects import SelectObjects

# Object Creation
from .create_meshes import CreateMeshes
from .create_armatures import CreateArmatures
from .create_curves import CreateCurves
from .create_lights import CreateLights
from .create_materials import CreateMaterials

# Object Editing
from .create_bones import CreateBones
from .create_modifiers import CreateModifiers
from .create_shapekeys import CreateShapeKeys
from .create_uvunwrap import CreateUVUnwrap
from .convert_objects import ConvertObjects
from .move_football import MoveFootballFields
from .rotate_circles import RotateCircles
from .create_faces import CreateFaces
from .create_edges import CreateEdges
from .merge_distance import MergeDistance
from .delete_faces import DeleteFaces
from .delete_edges import DeleteEdges
from .delete_vertices import DeleteVertices

# Nodes
from .create_nodes_compositor import CreateNodesCompositor
from .create_nodes_geometry import CreateNodesGeometry
from .create_nodes_shader import CreateNodesShader
from .create_geometrynodes import CreateGeometryNodes

# Rebder
from .render_images import RenderImages
from .render_animations import RenderAnimations
from .render_frames import RenderFrames
from .render_50p import Render50P
from .render_engine_eevee import RenderEngineEevee
from .render_engine_cycles import RenderEngineCycles
from .render_composite import RenderComposite

# Animation
from .keyframe_interp import KeyframeInterp
from .create_fcurvemodifiers import CreateFCurveModifiers

# Project
from .save_projects import SaveProjects
from .save_projectcopies import SaveProjectCopies
from .open_projects import OpenProjects
from .import_projects import ImportProjects

# Usage Time
from .time_used import TimeUsed


DAILY_ACHIEVEMENT_CLASSES: list[DailyAchievement] = [
    # General
    DoOperations,
    SelectObjects,

    # Object Creation
    CreateMeshes,
    CreateArmatures,
    CreateCurves,
    CreateLights,
    CreateMaterials,

    # Object Editing
    CreateBones,
    CreateModifiers,
    CreateShapeKeys,
    CreateUVUnwrap,
    ConvertObjects,
    MoveFootballFields,
    RotateCircles,
    CreateFaces,
    CreateEdges,
    MergeDistance,
    DeleteFaces,
    DeleteEdges,
    DeleteVertices,

    # Nodes
    CreateNodesCompositor,
    CreateNodesGeometry,
    CreateNodesShader,
    CreateGeometryNodes,

    # Animation
    KeyframeInterp,
    CreateFCurveModifiers,

    # Render
    RenderImages,
    RenderAnimations,
    RenderFrames,
    Render50P,
    RenderEngineEevee,
    RenderEngineCycles,
    RenderComposite,

    # Project
    SaveProjects,
    SaveProjectCopies,
    OpenProjects,
    ImportProjects,

    # Usage Time
    TimeUsed
]
