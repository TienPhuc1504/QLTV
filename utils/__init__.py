# Utils package

def treeview_sort_column(tree, col, reverse):
    """
    Sắp xếp Treeview theo cột
    - tree: Treeview widget
    - col: Tên cột cần sắp xếp
    - reverse: True = giảm dần, False = tăng dần
    """
    # Lấy tất cả dữ liệu
    data = [(tree.set(child, col), child) for child in tree.get_children('')]
    
    # Thử sắp xếp theo số, nếu không được thì sắp xếp theo chuỗi
    try:
        data.sort(key=lambda x: float(x[0].replace(',', '').replace('đ', '').replace('∞', '999999')), reverse=reverse)
    except (ValueError, TypeError):
        data.sort(key=lambda x: x[0].lower() if isinstance(x[0], str) else str(x[0]).lower(), reverse=reverse)
    
    # Di chuyển items theo thứ tự mới
    for index, (val, child) in enumerate(data):
        tree.move(child, '', index)
    
    # Đảo ngược cho lần click tiếp theo
    tree.heading(col, command=lambda: treeview_sort_column(tree, col, not reverse))