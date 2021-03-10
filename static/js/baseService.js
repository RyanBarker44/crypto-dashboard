
export const baseService = async (url, payload, success, errorCallback) => {
    const response = await $.ajax({
        url: url,
        contentType: 'application/json;charset=utf-8',
        data: JSON.stringify(payload),
        dataType: 'json',
        type: 'POST',
        success: (response) => {
            if (success) {
                success(response);
            }
        },
        error: (e) => {
            console.log(e)
        }
    });

    if (response && response.data) {
        return response.data;
    }

    return response;
};