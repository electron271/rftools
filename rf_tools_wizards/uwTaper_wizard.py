#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

# This python script wizard creates an arc track for microwave applications
# Author  easyw
# taskkill -im pcbnew.exe /f &  C:\KiCad-v5-nightly\bin\pcbnew

from __future__ import division

import math, cmath

from pcbnew import *
import pcbnew
import FootprintWizardBase


class uwTaper_wizard(FootprintWizardBase.FootprintWizard):

    def GetName(self):
        return "uW Taper Pad"

    def GetDescription(self):
        return "uW Taper Pad Footprint Wizard"

    def GenerateParameterList(self):

        self.AddParam("Taper", "P1 width", self.uMM, 0.5, min_value=0, hint="Pad 1 width")
        self.AddParam("Taper", "P1 height", self.uMM, 0.5, min_value=0, hint="Pad 1 height")
        self.AddParam("Taper", "P2 width", self.uMM, 1.0, min_value=0, hint="Pad 2 width")
        self.AddParam("Taper", "P2 height", self.uMM, 1.0, min_value=0, hint="Pad 2 height")
        self.AddParam("Taper", "P2 vert offset", self.uMM, 0.0, hint="Pad 2 vertical offset")
        self.AddParam("Taper", "length", self.uMM, 3.0, min_value=0, hint="length")
        self.AddParam("Taper", "solder_clearance", self.uMM, 0.0, min_value=0, hint="Solder Clearance")
        
    def CheckParameters(self):

        pads = self.parameters['Taper']
        

    def GetValue(self):
        name = "{0:.2f}_{1:0.2f}_{2:.2f}_{3:.2f}_{4:.2f}".format(pcbnew.ToMM(self.parameters["Taper"]["P1 width"]),\
               pcbnew.ToMM(self.parameters["Taper"]["P1 height"]),pcbnew.ToMM(self.parameters["Taper"]["P2 width"]),\
               pcbnew.ToMM(self.parameters["Taper"]["P2 height"]),pcbnew.ToMM(self.parameters["Taper"]["length"]))
        return "uwT" + "%s" % name
    
    def GetReferencePrefix(self):
        return "uwT" + "***"

    # build a custom pad
    def smdCustomPolyPad(self, module, size, pos, name, vpoints, layer, solder_clearance):
        # fix credit: MarwanOSayeds pr (#76) on the upstream repo
        # cherry picking this is a temporary fix until their PR is merged

        if hasattr(pcbnew, 'D_PAD'):
            pad = D_PAD(module)
        else:
            pad = PAD(module)
        #pad = PAD(module)
        ## NB pads must be the same size and have the same center
        pad.SetSize(size)
        #pad.SetSize(pcbnew.wxSize(size[0]/5,size[1]/5))
        pad.SetShape(PAD_SHAPE_CUSTOM) #PAD_RECT)
        pad.SetAttribute(PAD_ATTRIB_SMD) #PAD_SMD)
        #pad.SetDrillSize (0.)
        #Set only the copper layer without mask
        #since nothing is mounted on these pads
        #pad.SetPos0(wxPoint(0,0)) #pos)
        #pad.SetPosition(wxPoint(0,0)) #pos)
        #    pad.SetPos0(pos)
        pad.SetPosition(pos)
        #pad.SetOffset(pos)
        pad.SetPadName(name)
        #pad.Rotate(pos, angle)
        pad.SetAnchorPadShape(layer, PAD_SHAPE_RECT) #PAD_SHAPE_CIRCLE) #PAD_SHAPE_RECT)
        if solder_clearance > 0:
            pad.SetLocalSolderMaskMargin(solder_clearance)
            pad.SetLayerSet(pad.ConnSMDMask())
        else:
            layer_set_nonexposed=LSET()
            layer_set_nonexposed.addLayer(layer)
            pad.SetLayerSet(layer_set_nonexposed)
            #pad.SetLayerSet(LSET(base_seqVect(layer))) 
        
        if hasattr(pcbnew, 'D_PAD'): # kv5
            pad.AddPrimitive(vpoints,0) # (size[0]))
        else: #kv6-kv7
            if hasattr(pcbnew, 'EDA_RECT'): # kv5,kv6
                pad.AddPrimitivePoly(vpoints, 0, True) # (size[0]))
            else: # kv7
                pad.AddPrimitivePoly(layer,pcbnew.VECTOR_VECTOR2I(vpoints), 0, True) # (size[0]))
        return pad

    def smdPad(self,module,size,pos,name,ptype,angle_D,layer,solder_clearance,offs=None):
        if hasattr(pcbnew, 'D_PAD'):
            pad = D_PAD(module)
        else:
            pad = PAD(module)
        pad.SetSize(size)
        pad.SetShape(ptype)  #PAD_SHAPE_RECT PAD_SHAPE_OVAL PAD_SHAPE_TRAPEZOID PAD_SHAPE_CIRCLE 
        # PAD_ATTRIB_CONN PAD_ATTRIB_SMD
        pad.SetAttribute(PAD_ATTRIB_SMD)
        if solder_clearance > 0:
            pad.SetLocalSolderMaskMargin(solder_clearance)
            pad.SetLayerSet(pad.ConnSMDMask())
        else:
            layer_set_nonexposed=LSET()
            layer_set_nonexposed.addLayer(layer)
            pad.SetLayerSet(layer_set_nonexposed)
            #pad.SetLayerSet( LSET(base_seqVect(layer)) )
        #pad.SetDrillSize (0.)
        #pad.SetLayerSet(pad.ConnSMDMask())
        # pad.SetPos0(pos)
        pad.SetPosition(pos)
        #pad.SetOrientationDegrees(90-angle_D/10)
        pad.SetOrientationDegrees(angle_D)
        if offs is not None:
            pad.SetOffset(offs)
        pad.SetName(name)
        return pad

    def Polygon(self, points, layer):
            """
            Draw a polygon through specified points
            """
            import pcbnew
            
            polygon = pcbnew.EDGE_MODULE(self.module)
            polygon.SetWidth(0) #Disables outline

            polygon.SetLayer(layer)
            polygon.SetShape(pcbnew.S_POLYGON)

            polygon.SetPolyPoints(points)

            self.module.Add(polygon)
        
    def BuildThisFootprint(self):

        pads = self.parameters['Taper']
        
        width1 = pads['P1 width']
        width2 = pads['P2 width']
        height1 = pads['P1 height']
        height2 = pads['P2 height']
        length =  pads['length']
        p2vof = pads['P2 vert offset']
        sold_clear = pads['solder_clearance']
        w1=width1;w2=width2;
        h1=height1;h2=height2;
        module = self.module
        #  1   2  3  4
        #         +--+
        #        /   |
        #       /    |
        #9 +---+     |
        #  | +     + |
        #8 +---+     |
        #       \    |
        #        \   |
        #         +--+
        #      7  6  5
        points = [
                (-w1/2,-h1/2),
                (w1/2,-h1/2),
                (w1/2+length-w2/2,-h2/2-p2vof),
                (w1/2+length+w2/2,-h2/2-p2vof),
                (w1/2+length+w2/2,h2/2-p2vof),
                (w1/2+length-w2/2,h2/2-p2vof),
                (w1/2,h1/2),
                (-w1/2,h1/2),
                ]        
        #Last two points can be equal
        if points[-2] == points[-1]:
            points = points[:-1]
        
        if hasattr(pcbnew, 'EDA_RECT'): # kv5,kv6
            pos = pcbnew.wxPoint(0,0)
            offset1 = pcbnew.wxPoint(0,0)
            #offset2 = pcbnew.wxPoint(length+w1/2,0)
            offset2 = pcbnew.wxPoint(0,0)
            points = [wxPoint(*point) for point in points]
            vpoints = wxPoint_Vector(points)
        elif hasattr(pcbnew, 'wxPoint()'): # kv7:
            pos = pcbnew.VECTOR2I(wxPoint( 0,0 ))
            offset1 = pcbnew.VECTOR2I(wxPoint( 0,0 ))
            offset2 = pcbnew.VECTOR2I(wxPoint( 0,0 ))
            #points = [pcbnew.VECTOR2I(*wxPoint(point)) for point in points]
            pts=[]
            for point in points:
                newEle=VECTOR2I(wxPoint(point[0],point[1]))
                pts.append(newEle)
            points = pts
            vpoints = VECTOR_VECTOR2I(points)
            #vpoints = points
        else: # kv8
            pos = pcbnew.VECTOR2I(int(0),int(0))
            offset1 = pcbnew.VECTOR2I(int(0),int(0))
            offset2 = pcbnew.VECTOR2I(int(0),int(0))
            #points = [pcbnew.VECTOR2I(*wxPoint(point)) for point in points]
            pts=[]
            for point in points:
                newEle=VECTOR2I(int(point[0]),int(point[1]))
                pts.append(newEle)
            points = pts
            vpoints = VECTOR_VECTOR2I(points)
        # self.Polygon(points, F_Cu)

        #module.Add(self.smdPad(module, size_pad, pcbnew.wxPoint(0,0), "1", PAD_SHAPE_RECT,0,F_Cu,sold_clear,offset1))
        #solder clearance added only to polygon
        if hasattr(pcbnew, 'EDA_RECT'): # kv5,kv6
            size_pad = pcbnew.wxSize(width1, height1)
            module.Add(self.smdCustomPolyPad(module, size_pad, wxPoint(0,0), "1", vpoints,F_Cu,sold_clear))
            size_pad = pcbnew.wxSize(width2, height2)
            module.Add(self.smdPad(module, size_pad, pcbnew.wxPoint(length+w1/2,0-p2vof), "1", PAD_SHAPE_RECT,0,F_Cu,0.0,offset2))
        elif hasattr(pcbnew, 'wxPoint()'): # kv7:
            size_pad = pcbnew.VECTOR2I(width1, height1)
            module.Add(self.smdCustomPolyPad(module, size_pad, pcbnew.VECTOR2I(wxPoint(0,0)), "1", vpoints,F_Cu,sold_clear))
            size_pad = pcbnew.VECTOR2I(width2, height2)
            module.Add(self.smdPad(module, size_pad, pcbnew.VECTOR2I(wxPoint(length+w1/2,0-p2vof)), "1", PAD_SHAPE_RECT,0,F_Cu,0.0,offset2))
        else: # kv8
            size_pad = pcbnew.VECTOR2I(width1, height1)
            module.Add(self.smdCustomPolyPad(module, size_pad, pcbnew.VECTOR2I(int(0),int(0)), "1", vpoints,F_Cu,sold_clear))
            size_pad = pcbnew.VECTOR2I(width2, height2)
            module.Add(self.smdPad(module, size_pad, pcbnew.VECTOR2I(int(length+w1/2),int(0-p2vof)), "1", PAD_SHAPE_RECT,0,F_Cu,0.0,offset2))
        
        # Text size
        text_size = self.GetTextSize()  # IPC nominal
        thickness = self.GetTextThickness()
        textposy = self.draw.GetLineThickness()/2 + self.GetTextSize()/2 + thickness #+ outline['margin']
        height = max(height1,height2)
        self.draw.Reference( 0+length/2, -textposy-height/2, text_size )
        self.draw.Value( 0+length/2, textposy+height/2+text_size/2, text_size )
        # set SMD attribute
        if hasattr(pcbnew, 'MOD_VIRTUAL'):
            module.SetAttributes(pcbnew.MOD_VIRTUAL)
        else:
            module.SetAttributes(pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES)
        # module.SetAttributes(pcbnew.MOD_VIRTUAL)
        # module.SetAttributes(pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES)
        __version__ = 1.7
        self.buildmessages += ("version: {:.1f}".format(__version__))

uwTaper_wizard().register()
