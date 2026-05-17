import bpy
import math
import bpy_extras

# ブレンダーに登録するアドオン情報
bl_info = {
    "name": "レベルエディタ",
    "author": "Taro Kamata",
    "version": (1, 0),
    "blender": (3, 3, 1),
    "location": "",
    "description": "レベルエディタ",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"
}

# --- メニュークラス ---
class TOPBAR_MT_my_menu(bpy.types.Menu):
    bl_idname = "TOPBAR_MT_my_menu"
    bl_label = "MyMenu"
    bl_description = "拡張メニュー by " + bl_info["author"]

    def draw(self, context):
        layout = self.layout
        layout.operator(MYADDON_OT_stretch_vertex.bl_idname, text=MYADDON_OT_stretch_vertex.bl_label)
        layout.operator(MYADDON_OT_create_ico_sphere.bl_idname, text=MYADDON_OT_create_ico_sphere.bl_label)
        layout.separator() 
        layout.operator(MYADDON_OT_export_scene.bl_idname, text=MYADDON_OT_export_scene.bl_label)

    def submenu(self, context):
        self.layout.menu(TOPBAR_MT_my_menu.bl_idname)

# --- オペレータ：頂点を伸ばす ---
class MYADDON_OT_stretch_vertex(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_stretch_vertex"
    bl_label = "頂点を伸ばす"
    bl_description = "頂点座標を引っ張って伸ばします"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if "Cube" in bpy.data.objects:
            bpy.data.objects["Cube"].data.vertices[0].co.x += 1.0
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Cubeが見つかりません")
            return {'CANCELLED'}

# --- オペレータ：ICO球生成 ---
class MYADDON_OT_create_ico_sphere(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_create_object"
    bl_label = "ICO球生成"
    bl_description = "ICO球を生成します"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.mesh.primitive_ico_sphere_add()
        return {'FINISHED'}

# --- オペレータ：シーン出力（ExportHelper継承版） ---
class MYADDON_OT_export_scene(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    bl_idname = "myaddon.myaddon_ot_export_scene"
    bl_label = "シーン出力"
    bl_description = "シーン情報をExportします"

    # 資料より：出力するファイルの拡張子を指定
    filename_ext = ".scene"

    def write_and_print(self, file, str):
        """資料より：コンソールとファイルに同時に書き出す関数"""
        print(str)
        file.write(str + '\n')

    def parse_scene_recursive(self, file, object, level):
        """資料より：親子関係を辿る再帰関数（深さ優先探索）"""
        # 深さに応じてインデント（タブ）を作成
        indent = ''
        for i in range(level):
            indent += "\t"

        # オブジェクト名を出力
        self.write_and_print(file, indent + object.type + " - " + object.name)
        
        # トランスフォーム情報の抽出
        trans, rot, scale = object.matrix_local.decompose()
        rot = rot.to_euler()
        rot.x, rot.y, rot.z = [math.degrees(v) for v in rot]

        # 情報を書き込み
        self.write_and_print(file, indent + "Trans(%f,%f,%f)" % (trans.x, trans.y, trans.z))
        self.write_and_print(file, indent + "Rot(%f,%f,%f)" % (rot.x, rot.y, rot.z))
        self.write_and_print(file, indent + "Scale(%f,%f,%f)" % (scale.x, scale.y, scale.z))
        self.write_and_print(file, '') # 空行

        # 子オブジェクトに対して再帰呼び出し
        for child in object.children:
            self.parse_scene_recursive(file, child, level + 1)

    def export(self):
        """資料より：ファイル書き出しのメイン処理"""
        print("シーン情報出力開始... %r" % self.filepath)
        
        with open(self.filepath, "wt") as file:
            self.write_and_print(file, "SCENE")
            # ルートオブジェクト（親がいないもの）から探索開始
            for object in bpy.context.scene.objects:
                if object.parent is None:
                    self.parse_scene_recursive(file, object, 0)

    def execute(self, context):
        print("シーン情報をExportします")
        self.export() # ファイル書き出し実行
        
        self.report({'INFO'}, "シーン情報をExportしました")
        print("シーン情報をExportしました")
        return {'FINISHED'}

# --- 登録処理 ---
classes = (
    MYADDON_OT_stretch_vertex,
    MYADDON_OT_create_ico_sphere,
    MYADDON_OT_export_scene,
    TOPBAR_MT_my_menu,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_editor_menus.append(TOPBAR_MT_my_menu.submenu)
    print("レベルエディタが有効化されました。")

def unregister():
    bpy.types.TOPBAR_MT_editor_menus.remove(TOPBAR_MT_my_menu.submenu)
    for cls in classes:
        bpy.utils.unregister_class(cls)
    print("レベルエディタが無効化されました。")

if __name__ == "__main__":
    register()