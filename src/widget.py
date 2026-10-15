"""Win11 Net Speed Compact v1.0.0
Developed by Iqbal Mahmud: https://iqbalmahmud.com
"""
import ctypes, json, math, os, re, sys, threading, time, webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import colorchooser
import psutil
from PIL import Image, ImageDraw
import pystray

APP='Win11NetSpeedCompact'
APP_VERSION='1.0.0'
WEBSITE='https://iqbalmahmud.com'
CFG_DIR=Path(os.getenv('APPDATA',Path.home()))/APP
CFG_FILE=CFG_DIR/'settings.json'
DEFAULT={
 'x':None,'y':None,'width':220,'height':42,'opacity':0.96,
 'unit':'auto_bytes','interface':'All','interval_ms':500,
 'font_color':'#F8FAFC','font_weight':'semibold','font_size':9,
 'background':'#172033','border':'#334155','autostart':True,'first_run_complete':False,
 'topmost_refresh_ms':1500
}
UNITS=('auto_bytes','auto_bits','MBps','Mbps','KBps','Kbps')
WEIGHTS=('normal','semibold','bold')
HEX_COLOR=re.compile(r'#[0-9A-Fa-f]{6}')
MAX_CFG_BYTES=64*1024
ERROR_ALREADY_EXISTS=183
_MUTEX=None

if os.name=='nt':
    from ctypes import wintypes
    # Explicit prototypes: without them ctypes truncates 64-bit handles and
    # GetLastError() can be clobbered by the interpreter between calls.
    _K32=ctypes.WinDLL('kernel32',use_last_error=True)
    _K32.CreateMutexW.restype=wintypes.HANDLE;_K32.CreateMutexW.argtypes=(wintypes.LPVOID,wintypes.BOOL,wintypes.LPCWSTR)
    _U32=ctypes.WinDLL('user32',use_last_error=True)
    _U32.FindWindowW.restype=wintypes.HWND;_U32.FindWindowW.argtypes=(wintypes.LPCWSTR,wintypes.LPCWSTR)
    _U32.GetWindowRect.restype=wintypes.BOOL;_U32.GetWindowRect.argtypes=(wintypes.HWND,ctypes.POINTER(wintypes.RECT))
    _U32.SetWindowPos.restype=wintypes.BOOL;_U32.SetWindowPos.argtypes=(wintypes.HWND,wintypes.HWND,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,wintypes.UINT)

def single_instance():
    global _MUTEX
    if os.name!='nt': return True
    _MUTEX=_K32.CreateMutexW(None,False,'Local\\IqbalMahmud.Win11NetSpeedCompact.v3')
    return bool(_MUTEX) and ctypes.get_last_error()!=ERROR_ALREADY_EXISTS

def _clamp_int(v,default,lo,hi):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):return default
    return min(hi,max(lo,int(v)))
def sanitize_cfg(raw):
    """Treat settings.json as untrusted: keep only known keys with valid types and ranges."""
    c=DEFAULT.copy()
    if not isinstance(raw,dict):return c
    for k in ('x','y'):c[k]=_clamp_int(raw.get(k),None,-32768,32767)
    c['width']=_clamp_int(raw.get('width'),DEFAULT['width'],150,2000)
    c['height']=_clamp_int(raw.get('height'),DEFAULT['height'],30,400)
    c['interval_ms']=_clamp_int(raw.get('interval_ms'),DEFAULT['interval_ms'],200,10000)
    c['topmost_refresh_ms']=_clamp_int(raw.get('topmost_refresh_ms'),DEFAULT['topmost_refresh_ms'],500,60000)
    c['font_size']=_clamp_int(raw.get('font_size'),DEFAULT['font_size'],6,32)
    op=raw.get('opacity')
    # Opacity is floored at 0.2 so a bad value can never make the widget invisible.
    if not isinstance(op,bool) and isinstance(op,(int,float)) and math.isfinite(op):c['opacity']=min(1.0,max(0.2,float(op)))
    if raw.get('unit') in UNITS:c['unit']=raw['unit']
    if raw.get('font_weight') in WEIGHTS:c['font_weight']=raw['font_weight']
    for k in ('font_color','background','border'):
        if isinstance(raw.get(k),str) and HEX_COLOR.fullmatch(raw[k]):c[k]=raw[k]
    if isinstance(raw.get('interface'),str) and 0<len(raw['interface'])<=256:c['interface']=raw['interface']
    for k in ('autostart','first_run_complete'):
        if isinstance(raw.get(k),bool):c[k]=raw[k]
    return c

def load_cfg():
    try:
        if CFG_FILE.stat().st_size>MAX_CFG_BYTES:return DEFAULT.copy()
        return sanitize_cfg(json.loads(CFG_FILE.read_text(encoding='utf-8')))
    except (OSError,ValueError,RecursionError):return DEFAULT.copy()
def save_cfg(c):
    """Write atomically so a crash or power loss never leaves a truncated settings file."""
    try:
        CFG_DIR.mkdir(parents=True,exist_ok=True);tmp=CFG_FILE.with_name(CFG_FILE.name+'.tmp')
        tmp.write_text(json.dumps(c,indent=2),encoding='utf-8');os.replace(tmp,CFG_FILE)
        return True
    except OSError:return False
def counter(interface):
    if interface=='All':return psutil.net_io_counters()
    return psutil.net_io_counters(pernic=True).get(interface,psutil.net_io_counters())
def fmt_speed(n,mode):
    if mode=='MBps':return f'{n/1e6:.2f} MB/s'
    if mode=='Mbps':return f'{n*8/1e6:.2f} Mbps'
    if mode=='KBps':return f'{n/1e3:.1f} KB/s'
    if mode=='Kbps':return f'{n*8/1e3:.1f} Kbps'
    if mode=='auto_bits':
        n*=8
        for f,u in ((1e9,'Gbps'),(1e6,'Mbps'),(1e3,'Kbps')):
            if n>=f:return f'{n/f:.2f} {u}'
        return f'{n:.0f} bps'
    for f,u in ((1e9,'GB/s'),(1e6,'MB/s'),(1e3,'KB/s')):
        if n>=f:return f'{n/f:.2f} {u}'
    return f'{n:.0f} B/s'
def startup_command():
    """Build a quoted per-user startup command for source or frozen EXE mode."""
    if getattr(sys,'frozen',False):return f'"{Path(sys.executable).resolve()}"'
    executable=Path(sys.executable).resolve()
    # Prefer pythonw.exe to avoid a console at sign-in when launched from python.exe.
    if executable.name.lower()=='python.exe':
        candidate=executable.with_name('pythonw.exe')
        if candidate.exists():executable=candidate
    return f'"{executable}" "{Path(__file__).resolve()}"'

def set_autostart(enabled):
    """Set current-user startup only. Returns (success, message)."""
    if os.name!='nt':return False,'Auto-start is supported on Windows only.'
    try:
        import winreg
        path=r'Software\Microsoft\Windows\CurrentVersion\Run'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,path,0,winreg.KEY_SET_VALUE) as key:
            if enabled:winreg.SetValueEx(key,APP,0,winreg.REG_SZ,startup_command())
            else:
                try:winreg.DeleteValue(key,APP)
                except FileNotFoundError:pass
        return True,'enabled' if enabled else 'disabled'
    except OSError as exc:return False,f'Windows could not update startup: {exc}'

def remove_legacy_startup():
    """Remove only startup values created by earlier builds of this project."""
    if os.name!='nt':return
    try:
        import winreg
        path=r'Software\Microsoft\Windows\CurrentVersion\Run'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,path,0,winreg.KEY_SET_VALUE) as key:
            for legacy in ('Win11NetSpeedWidgetPro',):
                try:winreg.DeleteValue(key,legacy)
                except FileNotFoundError:pass
    except OSError:pass

def taskbar_default(width,height):
    if os.name=='nt':
        try:
            hwnd=_U32.FindWindowW('Shell_TrayWnd',None);r=wintypes.RECT()
            if hwnd and _U32.GetWindowRect(hwnd,ctypes.byref(r)):
                return max(r.left,r.right-width-90),r.top+max(0,(r.bottom-r.top-height)//2)
        except Exception:pass
    return 100,100

class CompactWidget:
    def __init__(self,root):
        self.root=root;self.cfg=load_cfg();self.closed=False;self.drag=None;self.guard_job=None
        remove_legacy_startup()
        if not self.cfg.get('first_run_complete',False):
            ok,_=set_autostart(True);self.cfg['autostart']=bool(ok);self.cfg['first_run_complete']=True;save_cfg(self.cfg)
        elif self.cfg.get('autostart',False):
            # Refresh the path in case the folder or EXE was moved after first run.
            ok,_=set_autostart(True);self.cfg['autostart']=bool(ok);save_cfg(self.cfg)
        self.last=counter(self.cfg['interface']);self.last_t=time.perf_counter()
        root.title('Win11 Net Speed Compact');root.overrideredirect(True);root.minsize(150,30)
        x,y=self.cfg['x'],self.cfg['y']
        if x is None or y is None:x,y=taskbar_default(self.cfg['width'],self.cfg['height'])
        root.geometry(f"{self.cfg['width']}x{self.cfg['height']}+{x}+{y}")
        root.attributes('-alpha',self.cfg['opacity']);root.attributes('-topmost',True)
        self.build();self.make_menu();self.bind();self.make_tray();self.apply_style();self.guard();self.tick()
    def build(self):
        self.card=tk.Frame(self.root,highlightthickness=1);self.card.pack(fill='both',expand=True)
        self.down=tk.Label(self.card,text='↓ 0 B/s',anchor='center')
        self.up=tk.Label(self.card,text='↑ 0 B/s',anchor='center')
        self.down.pack(side='left',fill='both',expand=True,padx=(5,2),pady=2)
        self.up.pack(side='left',fill='both',expand=True,padx=(2,5),pady=2)
    def bind(self):
        for w in (self.root,self.card,self.down,self.up):
            w.bind('<ButtonPress-1>',self.start_move);w.bind('<B1-Motion>',self.move);w.bind('<ButtonRelease-1>',self.end_move);w.bind('<Button-3>',self.popup)
        self.root.bind('<Control-MouseWheel>',self.resize_wheel)
    def make_menu(self):
        self.menu=tk.Menu(self.root,tearoff=0)
        units=tk.Menu(self.menu,tearoff=0);self.unit_var=tk.StringVar(value=self.cfg['unit'])
        for label,val in [('Auto bytes','auto_bytes'),('Auto bits','auto_bits'),('MB/s','MBps'),('Mbps','Mbps'),('KB/s','KBps'),('Kbps','Kbps')]:units.add_radiobutton(label=label,value=val,variable=self.unit_var,command=self.set_unit)
        self.menu.add_cascade(label='Speed unit',menu=units)
        adapters=tk.Menu(self.menu,tearoff=0);self.if_var=tk.StringVar(value=self.cfg['interface']);adapters.add_radiobutton(label='All interfaces',value='All',variable=self.if_var,command=self.set_interface)
        for name,st in psutil.net_if_stats().items():
            if st.isup:adapters.add_radiobutton(label=name,value=name,variable=self.if_var,command=self.set_interface)
        self.menu.add_cascade(label='Network interface',menu=adapters)
        colors=tk.Menu(self.menu,tearoff=0)
        for name,value in [('White','#F8FAFC'),('Black','#0F172A'),('Blue','#38BDF8'),('Green','#34D399'),('Purple','#A78BFA'),('Orange','#FB923C')]:colors.add_command(label=name,command=lambda c=value:self.set_color(c))
        colors.add_separator();colors.add_command(label='Custom…',command=self.custom_color);self.menu.add_cascade(label='Font color',menu=colors)
        weights=tk.Menu(self.menu,tearoff=0);self.weight_var=tk.StringVar(value=self.cfg['font_weight'])
        for name,value in [('Normal','normal'),('Semi-bold','semibold'),('Bold','bold')]:weights.add_radiobutton(label=name,value=value,variable=self.weight_var,command=self.set_weight)
        self.menu.add_cascade(label='Font weight',menu=weights)
        sizes=tk.Menu(self.menu,tearoff=0);self.size_var=tk.IntVar(value=self.cfg['font_size'])
        for n in (8,9,10,11,12):sizes.add_radiobutton(label=str(n),value=n,variable=self.size_var,command=self.set_size)
        self.menu.add_cascade(label='Font size',menu=sizes)
        self.menu.add_command(label='Background color…',command=self.custom_background)
        self.menu.add_command(label='Reset position to taskbar',command=self.reset_position)
        self.autostart_var=tk.BooleanVar(value=bool(self.cfg.get('autostart',True)));self.menu.add_checkbutton(label='Start with Windows',variable=self.autostart_var,command=self.toggle_autostart)
        self.menu.add_command(label='Open iqbalmahmud.com',command=lambda:webbrowser.open(WEBSITE))
        self.menu.add_separator();self.menu.add_command(label='Exit',command=self.quit)
    def font(self):
        fam='Segoe UI Semibold' if self.cfg['font_weight'] in ('semibold','bold') else 'Segoe UI'
        weight='bold' if self.cfg['font_weight']=='bold' else 'normal'
        return (fam,int(self.cfg['font_size']),weight)
    def apply_style(self):
        bg=self.cfg['background'];self.root.configure(bg=bg);self.card.configure(bg=bg,highlightbackground=self.cfg['border'])
        for w in (self.down,self.up):w.configure(bg=bg,fg=self.cfg['font_color'],font=self.font())
    def popup(self,e):self.menu.tk_popup(e.x_root,e.y_root)
    def start_move(self,e):self.drag=(e.x_root-self.root.winfo_x(),e.y_root-self.root.winfo_y());self.root.lift()
    def move(self,e):
        if self.drag:self.root.geometry(f'+{e.x_root-self.drag[0]}+{e.y_root-self.drag[1]}')
    def end_move(self,e):
        self.drag=None;self.cfg['x']=self.root.winfo_x();self.cfg['y']=self.root.winfo_y();save_cfg(self.cfg)
    def resize_wheel(self,e):
        d=10 if e.delta>0 else -10;self.cfg['width']=min(2000,max(150,self.root.winfo_width()+d));self.cfg['height']=min(400,max(30,self.root.winfo_height()+(2 if e.delta>0 else -2)));self.root.geometry(f"{self.cfg['width']}x{self.cfg['height']}");save_cfg(self.cfg)
    def set_unit(self):self.cfg['unit']=self.unit_var.get();save_cfg(self.cfg)
    def set_interface(self):self.cfg['interface']=self.if_var.get();self.last=counter(self.cfg['interface']);self.last_t=time.perf_counter();save_cfg(self.cfg)
    def set_color(self,c):self.cfg['font_color']=c;self.apply_style();save_cfg(self.cfg)
    def custom_color(self):
        c=colorchooser.askcolor(color=self.cfg['font_color'],title='Speed font color')[1]
        if c:self.set_color(c)
    def custom_background(self):
        c=colorchooser.askcolor(color=self.cfg['background'],title='Widget background')[1]
        if c:self.cfg['background']=c;self.apply_style();save_cfg(self.cfg)
    def set_weight(self):self.cfg['font_weight']=self.weight_var.get();self.apply_style();save_cfg(self.cfg)
    def set_size(self):self.cfg['font_size']=self.size_var.get();self.apply_style();save_cfg(self.cfg)
    def reset_position(self):
        x,y=taskbar_default(self.root.winfo_width(),self.root.winfo_height());self.root.geometry(f'+{x}+{y}');self.cfg.update(x=x,y=y);save_cfg(self.cfg)
    def toggle_autostart(self):
        requested=bool(self.autostart_var.get());ok,message=set_autostart(requested)
        self.cfg['autostart']=requested if ok else not requested
        self.autostart_var.set(self.cfg['autostart']);save_cfg(self.cfg)
        if not ok:
            from tkinter import messagebox
            messagebox.showerror('Startup setting',message,parent=self.root)

    def bring_to_front(self):
        if self.closed:return
        self.root.deiconify();self.root.attributes('-topmost',True);self.root.lift()
        if os.name=='nt':
            try:
                HWND_TOPMOST=wintypes.HWND(-1);flags=0x0001|0x0002|0x0010|0x0040
                _U32.SetWindowPos(self.root.winfo_id(),HWND_TOPMOST,0,0,0,0,flags)
            except Exception:pass
    def guard(self):
        if self.closed:return
        # Keep exactly one guard timer alive; never move or hide the widget.
        self.bring_to_front()
        self.guard_job=self.root.after(max(500,int(self.cfg['topmost_refresh_ms'])),self.guard)
    def tick(self):
        if self.closed:return
        now=time.perf_counter();cur=counter(self.cfg['interface']);dt=max(.05,now-self.last_t)
        down=max(0,(cur.bytes_recv-self.last.bytes_recv)/dt);up=max(0,(cur.bytes_sent-self.last.bytes_sent)/dt)
        self.down.configure(text='↓ '+fmt_speed(down,self.cfg['unit']));self.up.configure(text='↑ '+fmt_speed(up,self.cfg['unit']))
        self.last,self.last_t=cur,now;self.root.after(max(200,int(self.cfg['interval_ms'])),self.tick)
    def make_tray(self):
        im=Image.new('RGBA',(64,64),(23,32,51,255));d=ImageDraw.Draw(im);d.line((8,48,23,31,35,39,56,14),fill=(56,189,248),width=6)
        menu=pystray.Menu(pystray.MenuItem('Bring to front',lambda:self.root.after(0,self.bring_to_front),default=True),pystray.MenuItem('Exit',lambda:self.root.after(0,self.quit)))
        self.tray=pystray.Icon(APP,im,'Net Speed Compact · Iqbal Mahmud',menu);threading.Thread(target=self.tray.run,daemon=True).start()
    def quit(self):
        self.closed=True
        if self.guard_job:
            try:self.root.after_cancel(self.guard_job)
            except Exception:pass
        try:self.tray.stop()
        except Exception:pass
        self.root.destroy()

if __name__=='__main__':
    if not single_instance():sys.exit(0)
    root=tk.Tk();CompactWidget(root);root.mainloop()
