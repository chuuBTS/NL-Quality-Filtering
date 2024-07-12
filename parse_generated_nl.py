import json
import os
import ast


# 解析从GPT生成的自然语言查询结果，并将其保存为JSON格式
def parse_gpt_result(ori_gpt_result):

    gpt_result = ori_gpt_result
    if '```json' in gpt_result:
        gpt_result = gpt_result.split('```json')[1].split('```')[0]
        # gpt_result = json.loads(gpt_result)
        if '//' in gpt_result:
            # split by lines
            str_list = gpt_result.split('\n')
            for idx in range(len(str_list)):
                cur_str = str_list[idx]
                if '//' in cur_str:
                    str_list[idx] = cur_str.split('//')[0]
            gpt_result = '\n'.join(str_list)
        try:            
            gpt_result = ast.literal_eval(gpt_result)
            return gpt_result
        except:
            try:
                gpt_result = json.loads(gpt_result)
                return gpt_result
            except:
                print("can't parse 1: ", gpt_result)
                return None
    elif '### Output Format:' in gpt_result:
        gpt_result = gpt_result.split('### Output Format:')[1]
        if '```' in gpt_result:
            gpt_result = gpt_result.split('```', 1)[1].split('```')[0]
        else:
            gpt_result = gpt_result.split('{', 1)[1].split('}')[0]
            gpt_result = '{' + gpt_result + '}'
        if '//' in gpt_result:
            # split by lines
            str_list = gpt_result.split('\n')
            for idx in range(len(str_list)):
                cur_str = str_list[idx]
                if '//' in cur_str:
                    str_list[idx] = cur_str.split('//')[0]
            gpt_result = '\n'.join(str_list)
        
        gpt_result = ast.literal_eval(gpt_result)
        return gpt_result
    # ### Output:
    elif 'Output:' in gpt_result:
        gpt_result = gpt_result.split('Output:')[1]
        # if '```' in gpt_result:
        #     gpt_result = gpt_result.split('```', 1)[1].split('```')[0]
        # else:
        #     gpt_result = gpt_result.split('{', 1)[1].split('}')[0]
        #     gpt_result = '{' + gpt_result + '}'
        # if '//' in gpt_result:
        #     # split by lines
        #     str_list = gpt_result.split('\n')
        #     for idx in range(len(str_list)):
        #         cur_str = str_list[idx]
        #         if '//' in cur_str:
        #             str_list[idx] = cur_str.split('//')[0]
        #     gpt_result = '\n'.join(str_list)
        try:
            gpt_result = ast.literal_eval(gpt_result)
            return gpt_result
        except:
            try:
                gpt_result = json.loads(gpt_result)
                return gpt_result
            except:
                print("can't parse 1.2: ", gpt_result)
                return None
    elif '```' in gpt_result:
        gpt_result = gpt_result.split('```', 1)[1].split('```')[0]
        if '//' in gpt_result:
            # split by lines
            str_list = gpt_result.split('\n')
            for idx in range(len(str_list)):
                cur_str = str_list[idx]
                if '//' in cur_str:
                    str_list[idx] = cur_str.split('//')[0]
            gpt_result = '\n'.join(str_list)
        try:        
            gpt_result = ast.literal_eval(gpt_result)
            return gpt_result
        except:
            try:
                gpt_result = json.loads(gpt_result)
                return gpt_result
            except:
                print("can't parse 2: ", ori_gpt_result)
                return None
    # elif '{' in gpt_result:
    #     gpt_result = gpt_result.split('{', 1)[1].split('}')[0]
    #     gpt_result = '{' + gpt_result + '}'
    #     try:
    #         gpt_result = ast.literal_eval(gpt_result)
    #         return gpt_result
    #     except:
    #         try:
    #             gpt_result = json.loads(gpt_result)
    #             return gpt_result
    #         except:
    #             print("can't parse 3: ", ori_gpt_result)
    #             return None
    else:
        try:
            gpt_result = ast.literal_eval(gpt_result)
            return gpt_result
        except:
            try:
                gpt_result = json.loads(gpt_result)
                return gpt_result
            except:
                print("can't parse 4: ", ori_gpt_result)
                return None
        
if __name__ == "__main__":
    file_dir = './generated_nl_gpt/'
    save_dir = './generated_nl_gpt_json/'
    file_list = os.listdir(file_dir)
    file_list.sort()

    for filename in file_list:
        # print(filename)
        # if save path not exist
        if os.path.exists(save_dir + filename):
            continue

        load_json = json.load(open(file_dir + filename, 'r'))
        gpt_result = load_json['gpt_result']
        if isinstance(gpt_result, dict):
            # save
            save_json = load_json
            with open(save_dir + filename, 'w') as f:
                json.dump(save_json, f, indent=2)
            # print("save: ", save_dir + filename)
            # break

        else:
            #parse
            ori_gpt_result = gpt_result
            gpt_result = parse_gpt_result(gpt_result)
            if gpt_result is not None:
                # save
                save_json = load_json
                save_json['gpt_result'] = gpt_result
                with open(save_dir + filename, 'w') as f:
                    json.dump(save_json, f, indent=2)
            else:
                cur_dir = './generated_nl_cannot_parse/'
                save_path = cur_dir + filename
                with open(save_path, 'w') as f:
                    f.write(ori_gpt_result)
            #     # print("can't parse: ", ori_gpt_result)
            #     break
            #     print("==================================")
            #     print(ori_gpt_result)
            #     print("==================================")
            #     break


