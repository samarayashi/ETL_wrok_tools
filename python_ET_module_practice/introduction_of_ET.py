import xml.etree.ElementTree as ET
import lxml.etree
import copy

# ET模組常用內容要分成三類: ET.ElementTree物件、ET.Element物件，和直接從ET調用的方法
# 對整 XML 文件的操作一般是對ElementTree物件進行，而對 XML 結點的操作一般是對Element物件進行。

# ET.parse會回傳tree
# tree.getroot() 可以拿到這個tree的根節點 => 同時也就是一個element
#   而這tree和element有繼承關係，所以對root_element的內容做修改，tree的內容同時也修改了
#   所以對tree的內容元素做修改後，最終仍只要使用tree.write就可以得到修改過後的xml
workflow_tree = ET.parse('single_ext.xml')
workflow = workflow_tree.getroot()



# ET.parse('single_ext.xml')出來是一個個的物件，內容非基本型態
# 若照以下操作只會加入一個元素，因為都指向同一個物件
# for _ in range(3):
#   test_element.append(workflow)
workflow1 = copy.deepcopy(workflow)
workflow2 = copy.deepcopy(workflow)


# ##關於element
# 利用建構子建立元素 Element(tag, attrib={}, **extra)
# element有append()、remove()、insert()、等操作，可以查看文檔，
#    比較特別的是：append()是添加單一element，extend()是添加一個sequence的element，而insert可以指定index
# 常用屬性有：tag、text、attrib
# attrib以key-value pair存放，幾乎與字典形式無異
#   有各式可以修改、獲取key、value內容的方法如set()、get()、keys()、items()
# 元素查找分成find系列iter系列
#   find()、findall()、findtext() =>只往下找一層，參數match可以放入tag名或xpath路徑 => 並非支持完整xpath語法，文檔有寫支援部分
#   iter(tag=None)、iterfind(match, namespaces=None)、itertext() => 會遍歷底下子結構的每一層，找出所有相符的
# element還支持len()、和[]切片
# 要檢驗是否有該元素element = root.find('foo')
#   請用len(elem) 或 elem is None進行檢驗
#   不帶子元素的元素將被檢測為 False
#       因此若用if not element: 會包含element not found, or element has no subelements這兩種狀況
test_element = ET.Element('test')
test_element.append(workflow1)
test_element.append(workflow2)
print(len(test_element))

# 輸出方式一：把元素裝進ElementTree，使用其中的write方法
test_tree = ET.ElementTree(test_element)
test_tree.write("test.xml", encoding="utf-8")

# 輸出方式二：ET裡的tostring()把元素轉為字串
data = ET.tostring(test_element)
# 寫成檔案時要開byte模式
with open("test_to_string.xml", "wb") as file:
    file.write(data)

# 若想要打印出來的內容格式化
#   可以引用lxml package的etree模組，或是使用外部的文件編輯器直接修正
#   xml package則需要使用xml.dom.minidom

# 重新解析xml文件
test_tree2 = lxml.etree.parse("test_to_string.xml")
print("lxml package's etree object equals xml package's etree object:", test_tree == test_tree2)  # False
pretty = lxml.etree.tostring(test_tree2, encoding="utf-8", pretty_print=True)
with open("pretty_output.xml", "wb") as file:
    file.write(pretty)



# pretty = lxml.etree.tostring(test_tree, encoding="utf-8", pretty_print=True)
# with open("test_pretty_output.xml", "wb") as file:
#     file.write(pretty)

# ##補充關於ElementTree
# 提供查找方法，如同Element，只是從根部開始尋找
# 其他方法：parse()、getroot()、write()
#   parse()方法
#       調用ET.parse()是返回一個tree
#       ElementTree.parse()則是把內容載入該tree中

# ##補充ET中的函式
# 目前看到常用的有parse()、SubElement()、tostring()
#   若要在指定位置建立元素的話 => SubElement(parent, tag, attrib={}, **extra)，
# dump()直接將element利用sys.stdout輸出，拿來debug用 => 實際寫出還是要靠上面兩種方式
# indent() => 添加空格到子树来实现树的缩进效果。
# fromstring() 可以藉由string轉成element

# python官方文檔
# https://docs.python.org/zh-tw/3/library/xml.etree.elementtree.html#xml.etree.ElementTree.Element.remove