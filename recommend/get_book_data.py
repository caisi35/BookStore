from models import ToMongo


def get_data():
    try:
        my_conn = ToMongo()
        evaluates = my_conn.get_col('evaluate').find()
        results = {}
        for evaluate in evaluates:
            book_dist = {}
            evaluate_id = str(evaluate.get('_id'))
            # print(evaluate.get('_id'))
            comment_dist = {}
            for comment in evaluate.get('comment'):
                # print(comment)
                user_id = str(comment.get('user_id'))
                comment_dist[user_id] = comment.get('star')
                # print(comment.get('user_id'), comment.get('star'))
            results[evaluate_id] = comment_dist
            # results.append(book_dist)
        # print(results)
        return results
    except Exception as e:
        print(e)
        return


if __name__ == '__main__':
    result = get_data()
    # for i in result:
    #     print(i)