from pathlib import Path
import subprocess


def bin2_txt(output_path: Path):
    ipath = output_path + 'sfm_superpoint+superglue'
    opath = output_path + 'sparse'
    cmd = ['colmap model_converter', ipath, opath, '--output_type TXT']
    subprocess.run(' '.join(cmd), check=True, shell=True)


def bin2_ply(output_path: Path):
    ipath = output_path + 'sfm_superpoint+superglue'
    opath = output_path + 'dense/model.ply'
    cmd = ['colmap model_converter', ipath, opath, '--output_type PLY']
    subprocess.run(' '.join(cmd), check=True, shell=True)


def undistorter(image_path: Path, output_path: Path, max_image_size):
    ipath = output_path + 'sfm_superpoint+superglue'
    opath = output_path + 'dense'
    cmd = ['colmap image_undistorter',
           '--image_path', image_path,
           '--input_path', ipath,
           '--output_path', opath,
           '--max_image_size', max_image_size]
    subprocess.run(' '.join(cmd), check=True, shell=True)


def patch_match_stereo(output_path: Path, max_image_size, window_radius, filter_min_ncc):
    wpath = output_path + 'dense'
    cmd = ['colmap patch_match_stereo',
           '--workspace_path', wpath,
           '--workspace_format', 'COLMAP',
           '--PatchMatchStereo.max_image_size', max_image_size,
           '--PatchMatchStereo.window_radius', window_radius,
           '--PatchMatchStereo.geom_consistency', 'true',
           '--PatchMatchStereo.filter_min_ncc', filter_min_ncc]
    subprocess.run(' '.join(cmd), check=True, shell=True)


def stereo_fusion(output_path: Path):
    wpath = output_path + 'dense'
    cmd = ['colmap stereo_fusion',
           '--workspace_path', wpath,
           '--workspace_format', 'COLMAP',
           '--input_type', 'geometric',
           '--output_path', wpath + '/fused.py']
    subprocess.run(' '.join(cmd), check=True, shell=True)


def poisson_mesher(output_path: Path):
    ipath = output_path + 'dense'
    cmd = ['colmap poisson_mesher',
           '--input_path', ipath + '/fused.ply',
           '--output_path', ipath + '/poisson_mesher.ply']
    subprocess.run(' '.join(cmd), check=True, shell=True)


def dulaunay_mesher(output_path: Path):
    ipath = output_path + 'dense'
    cmd = ['colmap poisson_mesher',
           '--input_path', ipath,
           '--output_path', ipath + '/dulaunay_mesher.ply']
    subprocess.run(' '.join(cmd), check=True, shell=True)
