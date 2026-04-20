document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.search-filter').forEach(function (sel) {
        sel.addEventListener('change', function () {
            var option = this.options[this.selectedIndex];
            var paramName = option.getAttribute('data-name');
            var paramValue = this.value;

            var url = new URL(window.location.href);

            if (paramName && paramValue) {
                url.searchParams.set(paramName, paramValue);
            } else {
                // Сброс — удаляем параметры этого фильтра
                var fieldName = this.getAttribute('data-name');
                var toDelete = [];
                url.searchParams.forEach(function (v, k) {
                    if (k.indexOf(fieldName) === 0) toDelete.push(k);
                });
                toDelete.forEach(function (k) { url.searchParams.delete(k); });
            }

            window.location.href = url.toString();
        });
    });
});
