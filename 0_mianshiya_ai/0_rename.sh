find . -type f -name "* - 面试鸭*" -print0 | while IFS= read -r -d '' file; do
    dir=$(dirname "$file")
    base=$(basename "$file")
    newbase="${base/ - 面试鸭*/}"
    if [[ -n "$newbase" ]]; then
        mv -- "$file" "$dir/$newbase".html
    else
        echo "警告：跳过空文件名：$file"
    fi
done