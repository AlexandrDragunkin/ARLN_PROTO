# -*- coding: cp1251 -*-

''' ����� ������� �������� ������� ��� �������
'''
import machine
import math
vpi=3.1415926535897932384626433832795         # ����� Pi
eps_d = 0.001 # ���������� ����������

degrees = lambda f: f*180/vpi # ������ math ����������� ������� � �������
iif = lambda cond,if_true,if_false : if_true if cond else if_false

def GetDrillPlane(d):
    '''������� ������� ������, � ������ ��������� ���������
                
    d - ���������
    ������� ���������� ������� ���������: A,B,C,D,E,F ���� ��������� ��������, �� ������� �

    ���� ��������� ����������� ��� ����� � ����� ��� ������, ������� ���������� X
    '''
    z=d.position.z
    h=d.depth
    alpha=d.alfa
    beta=d.beta
    t=d.panel.thickness
    if (abs(beta)<eps_d or abs(beta-vpi)<eps_d):    # ��������� � ������
        if (z<=0 and h+abs(z)>=t or z>=t):
            return "A"
        else:
            return "F"
    if (abs(alpha)<eps_d):
        return "B"
    if (abs(alpha-vpi)<eps_d):
        return "C"
    if (abs(alpha-vpi/2)<eps_d):
        return "D"
    if (abs(alpha+vpi/2)<eps_d):
        return "E"
    return "X"

def GetDrillTrough(d):
    '''������� ������� �������������� �������� ��� ���������
    
    d - ���������
    
    ���������� True ���� ��������
    ��� False ���� ������
    '''
    if (d.depth-d.panel.thiknessPanel)>-eps_d and (GetDrillPlane(d) in ['A','F']):
        return True
    else:
        return False
        
def GetSlotDirection(slot):
    '''���������� ����������� �������
    ����������:
    "X" - ���� ������ ����� ��� X
    "Y" - ���� ������ ����� ��� Y
    �����, ���� ������ ��� �����, �� "A"
    '''
    if (abs(slot.start.x-slot.end.x)<eps_d):
        return "Y"
    if (abs(slot.start.y-slot.end.y)<eps_d):
        return "X"
    return "A"

def CheckGabs(panel,xmin,xmax,ymin,ymax,zmin,zmax):
    '''�������� ������ �� ����������� ����� �� ���������.
    
    panel - ������
    xmin, xmax; ymin,ymax; zmin,zmax - ����������� � �����������-����������
    �������� �� ��������������� ����
    
    ������� ���������� True, ���� ��� �������� �� ��������� � False, ���� �� ��������.
    ���� ���������� ���� �� �������, �� ��������� ��������������� ���������
    '''    
    b = panel.bounding_box
    if (b.max.x-b.min.x>xmax or b.max.x-b.min.x<xmin):
        print("������ #",panel.common_pos," (",panel.name,") �� �������� �� ��������� X(",b.max.x-b.min.x,")")
        print("�������� ������: ", b.max.x,b.max.y)
        return False
    if (b.max.y-b.min.y>ymax or b.max.y-b.min.y<ymin):
        print("������ #",panel.common_pos," (",panel.name,") �� �������� �� ��������� Y(",b.max.y-b.min.y,")")
        print("�������� ������: ", b.max.x,b.max.y)
        return False
    if (panel.thickness>zmax or panel.thickness<zmin):
        print("������ #",panel.common_pos," (",panel.name,") �� �������� �� ��������� Z(",panel.thickness,")")
        return False
    return True

# �������� ��� ����� ���� �������� � �������� ����� ��������
# � �������� ������� ���������� �������� r ���� MirrSegment 
# ���������� ��������� � �������� ����� ���� machine.Point2d()
class MirrSegment():
    def __init__(self):
        self.start_pt = machine.Point2d()
        self.end_pt = machine.Point2d()
        
def addSegmentMirrSegment(s):
    '''C������ ����� �������� r    � �������� �������, ������� ����� ������ � ������� �� ������� start_pt end_pt'''
    s.r = MirrSegment()
    s.r.start_pt.x, s.r.start_pt.y, s.r.end_pt.x, s.r.end_pt.y    =\
    s.start_pt.x , s.start_pt.y, s.end_pt.x ,    s.end_pt.y     
    
def SegmentReverse(segment):
    '''������ ������� ���������� �������� � ��������� ����� ��������.
    segment - ������� ������� 
    '''
    addSegmentMirrSegment(segment) # C������ ����� �������� r    � �������� �������
    if segment.path.overt:    # ���� ������ ��������� ��������� Overturn 
        segment.r.start_pt.x, segment.r.start_pt.y, segment.r.end_pt.x,        segment.r.end_pt.y    = \
        segment.end_pt.x ,    segment.end_pt.y ,    segment.start_pt.x , segment.start_pt.y 
    
def findMinPointInSegments(list_segments):
        '''������� ����������� ����� � ������ ���������
        list_segments = self.millingTech[index_path].segments
        '''
        i=0
        pos=[]
        dcx=99999999999
     
        for s in list_segments:
                #print round(s.start_pt.x,3)," ",round(s.start_pt.y,3)," ",round(s.end_pt.x,3)," ",round(s.end_pt.y,3)
                if s.start_pt.x<=dcx:
                        if s.start_pt.x==dcx:
                                pos=pos[len(pos)-1:]
                        pos.append(i)
                        #print i
                        dcx=s.start_pt.x
                i+=1
        #print pos
        if len(pos)>0:
                dcy=99999999999
                for i in pos:
                        s = list_segments[i]
                        if s.start_pt.y<dcy:
                                ps=i
        else:
                ps = pos[0]
        return ps

#--------------------------------------------------------

def findMaxPointInSegments(list_segments):
        '''������� ������������ ����� � ������ ���������
        index_path=0
        list_segments = self.millingTech[index_path].segments
        ps = findMinPointInSegments(list_segments)
        print ps
        print '------------------'
        ps = findMaxPointInSegments(list_segments)
        print ps
        print '------------------'
        '''
        i=0
        pos=[]
        dcx=-99999999999
     
        for s in list_segments:
            #print round(s.start_pt.x,3)," ",round(s.start_pt.y,3)," ",round(s.end_pt.x,3)," ",round(s.end_pt.y,3)
            if s.start_pt.x>=dcx:
                    if s.start_pt.x==dcx:
                            pos=pos[len(pos)-1:]
                    pos.append(i)
                    #print i
                    dcx=s.start_pt.x
            i+=1
        #print pos
        if len(pos)>0:
            dcy=-99999999999
            for i in pos:
                    s = list_segments[i]
                    if s.start_pt.y>dcy:
                            ps=i
        else:
            ps = pos[0]
        return ps
#---------------------------------------------------------

def findMaxLongSegment(list_segments):
    '''���������� ������ ������������� �� ������ ��������'''
    i=0
    clg=0
    pos=[]
    lensg=0.0
    for s in list_segments:
        leng_s=lengSegment(s)
        if leng_s>lensg:
            clg=i
            lensg=leng_s
        i+=1
    return clg
#---------------------------------------------------------

def checkMaxLongSegments(segments):
    '''�������� ������������������ ������� �� ��������� 
    ��� ����������� ���� ������������ �� ������ ����� ��� ������� � �������� � ���� �����'''
    ps=findMaxLongSegment(segments)
    sg=segments[ps].Divide(0.5)
    ts=segments[:ps]
    ts.extend(sg)
    ts.extend(segments[ps+1:])
    segments=ts
    return ps+1,segments
#--------------------------------------------------------

def angleGet( v1, v2):
    '''���������� ���� ����� ����� ���������
        v1 =con.tangent(1)
        v2 =con.tangent(0)
        res=angleGet(v1, v2)
    '''
    cc = round((v1%v2)/(v1.length()*v2.length()),3)
    cs = round(degrees(math.acos(cc)),0.01)
    return cs
#--------------------------------------------------------

def lengSegment(con):
    '''���������� ����� �������� ��� None'''
    res=None
    if type(con)==machine.Arc:
        v1 =con.tangent(1)
        v2 =con.tangent(0)
        res=vpi*con.radius*(angleGet(v1, v2))/180
    elif type(con)==machine.Line:
        vx=con.end_pt.x-con.start_pt.x
        vy=con.end_pt.y-con.start_pt.y
        vt=machine.Vector2d(vx,vy) 
        res=vt.length
    return res
#--------------------------------------------------------

def checkSegments(segments,outer):
    '''�������� ������������������ ������� �� ��������� 
    ��� �������� ������� ������� � ����������� ����� �� XY
    ��� ����������� ���� ������������ �� ������ ����� ��� ������� � �������� � ���� �����'''
    list_segments = segments
    if outer:
        ps = findMinPointInSegments(list_segments)
    else:
        ps, list_segments = checkMaxLongSegments(list_segments)
    segments=list_segments[ps:]
    segments.extend(list_segments[:ps])
    return segments
