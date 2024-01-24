import pickle

from . import set_logging_debug, logger
from .localization import RetrievalLocalizer, PoseLocalizer
from .utils.data import Paths, create_argparser, parse_paths, parse_conf
from .utils.io import write_pose_results
from .utils.eval import evaluate
from .settings import DATA_PATH

default_paths = Paths(
    query_images='images/images_upright/',
    reference_images='images/images_upright/',
    reference_sfm='sfm_superpoint+superglue/',
    query_list='query_list_with_intrinsics.txt',
    global_descriptors='global-feats-netvlad.h5',
    retrieval_pairs='pairs-query-netvlad.txt',
    results='pixloc_outputs.txt',
)

experiment = 'pixloc_megadepth'

default_confs = {
    'from_retrieval': {
        'experiment': experiment,
        'features': {},
        'optimizer': {
            'num_iters': 150,
            'pad': 1,
        },
        'refinement': {
            'num_dbs': 3,
            'multiscale': [4, 1],
            'point_selection': 'all',
            'normalize_descriptors': True,
            'average_observations': False,
            'do_pose_approximation': True,
        },
    },
    'from_poses': {
        'experiment': experiment,
        'features': {'preprocessing': {'resize': 1600}},
        'optimizer': {
            'num_iters': 50,
            'pad': 1,
        },
        'refinement': {
            'num_dbs': 5,
            'min_points_opt': 100,
            'point_selection': 'inliers',
            'normalize_descriptors': True,
            'average_observations': True,
            'layer_indices': [0, 1],
        },
    },
}


def main():
    parser = create_argparser('')
    parser.add_argument('--scene', nargs='+')
    parser.add_argument('--eval_only', action='store_true')
    args = parser.parse_intermixed_args()

    set_logging_debug(args.verbose)
    paths = parse_paths(args, default_paths)
    conf = parse_conf(args, default_confs)

    # 定位过程
    all_poses = {}
    for scene in args.scene:
        logger.info('Working on scene %s.', scene)
        paths_scene = paths.interpolate(scene=scene)

        # 结果已经输出 利用参数--eval_only跳过再次定位 直接观察结果
        if args.eval_only and paths_scene.results.exists():
            all_poses[scene] = paths_scene.results
            continue
        if args.from_poses:
            localizer = PoseLocalizer(paths, conf)
        else:
            localizer = RetrievalLocalizer(paths, conf)
        # 定位入口
        poses, logs = localizer.run_batched(skip=args.skip)
        # 结果输出
        write_pose_results(poses, paths_scene.results,
                           prepend_camera_name=True)
        with open(f'{paths_scene.results}_logs.pkl', 'wb') as f:
            pickle.dump(logs, f)
        all_poses[scene] = poses

    # 精度评定
    ground_truth = paths_scene.ground_truth
    paths_scene = paths.interpolate(scene=args.scene)
    logger.info('Evaluate scene %s: %s', scene, paths_scene.results)
    out = args.scene[0] + '_outputs'
    list_test = DATA_PATH / out / 'list_test.txt'
    evaluate(ground_truth, all_poses[scene],
             list_test,
             only_localized=(args.skip is not None and args.skip > 1))


if __name__ == '__main__':
    main()
