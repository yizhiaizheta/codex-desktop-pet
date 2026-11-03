"""Decode VP9 alpha explicitly; the default VP9 decoder may discard alpha."""
import os,subprocess,sys,shutil
from pathlib import Path
from platform_support import resource_root

def alpha_cleanup_mode():
    """Version cache entries and allow reverting to the original alpha."""
    return None if os.environ.get('BAILONG_ALPHA_CLEANUP')=='0' else 'gentle-v1'

def ffmpeg_path():
    root=resource_root()
    for candidate in (root/'tools/ffmpeg.exe',root/'tools/ffmpeg',root/'work/video-deps/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'):
        if candidate.is_file():return str(candidate)
    found=shutil.which('ffmpeg')
    if found:return found
    raise RuntimeError('缺少透明动画播放器，请重新完整解压桌宠安装包。')

def rgba_frames(path,size):
    filters=f'scale={size}:{size}:flags=lanczos'
    if alpha_cleanup_mode():
        # Keep the RGB resampling unchanged. Only constrain faint alpha to
        # the neighbourhood of solid details, with a soft two-pixel margin.
        # Strong alpha (including thin hairs and detached sparkles) is kept.
        filters+=(
            ',format=rgba,split=2[colors][mask];'
            '[mask]alphaextract,split=2[alpha][core];'
            "[core]lut=y='if(gte(val,224),255,0)',dilation,dilation,gblur=sigma=0.5[support];"
            "[alpha][support]blend=all_expr='if(lt(A,8),0,if(gte(A,224),A,min(A,B)))'[clean];"
            '[colors][clean]alphamerge,format=rgba'
        )
    args=[ffmpeg_path(),'-hide_banner','-loglevel','error','-threads','2','-filter_threads','2','-c:v','libvpx-vp9','-i',str(path),'-an','-vf',filters,'-pix_fmt','rgba','-f','rawvideo','pipe:1']
    kwargs={'creationflags':subprocess.CREATE_NO_WINDOW} if sys.platform=='win32' else {}
    with subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,**kwargs) as proc:
        try:
            stride=size*size*4
            while True:
                raw=proc.stdout.read(stride)
                if not raw:break
                if len(raw)!=stride:raise RuntimeError('动画帧不完整：'+str(path))
                yield raw
            error=proc.stderr.read().decode('utf-8',errors='replace')
            if proc.wait()!=0:raise RuntimeError('透明动画读取失败：'+error[-1000:])
        finally:
            if proc.poll() is None:proc.kill();proc.wait()
