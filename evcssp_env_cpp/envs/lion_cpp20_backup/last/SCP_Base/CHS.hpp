#pragma clang diagnostic push
#pragma ide diagnostic ignored "cppcoreguidelines-pro-type-member-init"
#pragma clang diagnostic ignored "-Wunknown-pragmas"
#pragma ide diagnostic ignored "cert-msc50-cpp"
#pragma ide diagnostic ignored "cert-msc51-cpp"
#pragma ide diagnostic ignored "bugprone-integer-division"
#pragma ide diagnostic ignored "OCUnusedGlobalDeclarationInspection"
#pragma ide diagnostic ignored "cppcoreguidelines-narrowing-conversions"


#ifndef LION_CPP20_SCP_H
#define LION_CPP20_SCP_H

#include <cmath>
#include <iostream>
#include <string>
#include <map>
#include <utility>
#include <vector>
#include <tuple>


std::vector<std::vector<double>> car_flow_possibility_list;
bool Use_Seed = true;
std::default_random_engine e;

void Change_Use_Seed(bool seed_input) {
    Use_Seed = seed_input;
}


// tested
class RandomUtil {
public:
    static float uniform_rand(float rand_start, float rand_end, bool seed = true) {
        int N = 999;
        if (seed and Use_Seed) {
            srand(time(nullptr));
            Use_Seed = false;
        }
        float tr = rand() % (N + 1) / (float) (N);
        tr = tr * (rand_end - rand_start) + rand_start;
        return tr;
    }
};

// tested
class PrintUtil {
public:
    template<typename T1, typename T2, typename T3>
    static void Print_Two_Dimension_Map(std::map<T1, std::map<T2, T3>> &map_to_print) {
        std::cout << "the two dimension map is" << std::endl;
        for (auto &it_one: map_to_print) {
            std::cout << "key_one = " << it_one.first << std::endl;
            for (auto &it_second: it_one.second) {
                std::cout << "key_second = " << it_second.first << " value = " << it_second.second << std::endl;
            }
        }
        std::cout << std::endl;
    }

    template<typename T1, typename T2>
    static void Print_Map(std::map<T1, T2> &map_to_print) {
        std::cout << "the map is" << std::endl;
        for (auto &it: map_to_print) {
            std::cout << "key = " << it.first << " value = " << it.second << std::endl;
        }
        std::cout << std::endl;
    }

    template<typename T>
    static void Print_Vector(std::vector<T> &v) {
        std::cout << "the vector is" << std::endl;
        for (T &it: v) {
            std::cout << it << " ";
        }
        std::cout << std::endl;
    }

    template<typename T>
    static void Print_Two_Dimension_Vector(std::vector<std::vector<T>> &vector_to_print) {
        std::cout << "the two dimension vector is" << std::endl;
        for (auto &temp: vector_to_print) {
            for (auto &te: temp) {
                std::cout << te << " ";
            }
            std::cout << std::endl;
        }
    }
};

// tested
class Read2Vector {
public:
    template<typename T>
    static int read(const std::string &data_to_read, std::vector<std::vector<T> > &a) {
        std::vector<T> b;
        std::vector<std::string> row;
        std::string line;
        std::string filename;
        std::ifstream in(data_to_read);
        if (in.fail()) {
            std::cout << "File not found" << std::endl;
            return 1;
        }
        while (getline(in, line) && in.good()) {
            file_to_string(row, line, ',');  //把line里的单元格数字字符提取出来，“,”为单元格分隔符
            for (auto &i: row) {
                b.push_back(string_to_float(i));
            }
            a.push_back(b);
            b.clear();
        }
        in.close();
        return 0;
    };

    static void file_to_string(std::vector<std::string> &record, const std::string &line, char delimiter) {
        int linepos = 0;
        char c;
        int line_max = line.length();
        std::string cur_string;
        record.clear();
        while (linepos < line_max) {
            c = line[linepos];
            if (isdigit(c) || c == '.') {
                cur_string += c;
            } else if (c == delimiter && !cur_string.empty()) {
                record.push_back(cur_string);
                cur_string = "";
            }
            ++linepos;
        }
        if (!cur_string.empty())
            record.push_back(cur_string);
    };

    static float string_to_float(std::string str) {
        int i = 0, len = str.length();
        float sum = 0;
        while (i < len) {
            if (str[i] == '.') break;
            sum = sum * 10 + str[i] - '0';
            ++i;
        }
        ++i;
        float t, d = 1;
        while (i < len) {
            d *= 0.1;
            t = str[i] - '0';
            sum += t * d;
            ++i;
        }
        return sum;
    };

    static void generate() {
        std::random_device rd; //obtain a seed
        std::mt19937 gen(rd()); //mersenne_twister_engine
        std::uniform_real_distribution<> dist(-1.0, 1.0);

        std::ofstream outFile;
        outFile.open("test5000.csv", std::ios::out);
        // 5000*128
        for (int i = 1; i <= 5000; i++) {
            for (int j = 1; j <= 127; j++) {
                outFile << dist(gen) << ',';
            }
            outFile << dist(gen) << std::endl;
        }
        outFile.close();
    };
};

int no_use = Read2Vector::read("car_flow_possibility_list_save.csv", car_flow_possibility_list);

// tested
class Station { // NOLINT(cppcoreguidelines-pro-type-member-init)
public:
    int charge_number;
    std::map<std::string, std::map<int, float>> situation;
    int station_time_hole;
    float load_assigned;
    std::vector<int> flow_in_number;
    std::vector<int> no_charge_list;
    int no_charge_number;
    std::vector<int> empty_list;
    int empty_number;
    float min_power;
    float max_power;
    float charge_power;
    int car_number;
    bool show;
    bool wait;
    int line;
    bool constant_charging;
    int max_line = 10;


    virtual void print_situation() {
        std::cout << "virtual print_situation" << std::endl;
    };
protected:
    void make_init_list() {
        std::map<int, float> list1;
        std::map<int, float> list2;
        std::map<int, float> list3;
        std::map<int, float> list4;
        std::map<int, float> list5;
        std::map<int, float> list6;
        std::map<int, float> list7;
        std::map<int, float> list8;
        for (int i = 0; i < this->charge_number; i++) {
            list1.insert(std::make_pair(i, 0.0));// 是否有车
            list2.insert(std::make_pair(i, 0.0));// 是否充电
            list3.insert(std::make_pair(i, 0.0));// 紧急度
            list4.insert(std::make_pair(i, 0.0));// 分配
            list5.insert(std::make_pair(i, 0.0));// 充电功率
            list6.insert(std::make_pair(i, 0.0));// soc
            list7.insert(std::make_pair(i, 0.0));// init_soc
            list8.insert(std::make_pair(i, 0.0));// target_soc
        }
        this->situation.insert(std::make_pair("car", list1));
        this->situation.insert(std::make_pair("charge", list2));
        this->situation.insert(std::make_pair("emergency", list3));
        this->situation.insert(std::make_pair("assign", list4));
        this->situation.insert(std::make_pair("power", list5));
        this->situation.insert(std::make_pair("soc", list6));
        this->situation.insert(std::make_pair("init_soc", list7));
        this->situation.insert(std::make_pair("target_soc", list8));
    };
};

// tested
class ChargePositionBase {
public:
    int position;
    Station *station_name;
    float arrive_soc;
    float target_soc;
    float current_soc;
    float current_power;
    bool must_charge;
    float emergency;
    int stay_time;
    int already_stay_time;

    ChargePositionBase() {
        std::cout << "no use any" << std::endl;
    };

    ChargePositionBase(int position_input, Station *station_name_input) {
        this->position = position_input;
        this->station_name = station_name_input;
        this->arrive_soc = -1;
        this->target_soc = -1;
        this->current_soc = -1;
        this->current_power = -1;
        this->must_charge = false;
        this->emergency = -1;
        this->stay_time = -1;
        this->already_stay_time = -1;
    };

    void pl_reset() {
        this->arrive_soc = -1;
        this->target_soc = -1;
        this->current_soc = -1;
        this->current_power = -1;
        this->must_charge = false;
        this->emergency = -1;
        this->stay_time = -1;
        this->already_stay_time = -1;
    };

    void reset_position() {
        this->station_name->situation["car"][this->position] = 0;
        this->station_name->situation["charge"][this->position] = 0;
        this->station_name->situation["emergency"][this->position] = 0;
        this->station_name->situation["assign"][this->position] = 0;
        this->station_name->situation["power"][this->position] = 0;
        this->station_name->situation["soc"][this->position] = 0;
        this->station_name->situation["init_soc"][this->position] = 0;
        this->station_name->situation["target_soc"][this->position] = 0;
        this->pl_reset();
    };

    void occupy_charge() const {
        if (this->station_name->situation["car"][this->position] == 1) {
            this->station_name->situation["charge"][this->position] = 1;
        } else {
            std::cout << "position " << this->position << " has no car" << std::endl;
        }
    };

    virtual void add_car() {
        std::cout << "virtual add_car" << std::endl;
    };

    virtual void calculate_needed() {
        std::cout << "virtual calculate_needed" << std::endl;
    };

    virtual void car_step() {
        std::cout << "virtual car_step" << std::endl;
    };


    virtual void remove_car(bool quick_leave) {
        std::cout << "virtual remove_car considering quick leave" << std::endl;
    };

protected:
    void occupy_position() const {
        this->station_name->situation["car"][this->position] = 1;
        this->station_name->situation["assign"][this->position] = 0;
    };
};

// tested
class StationBase : public Station {
public:
    StationBase(int charge_number, const std::string &position_class, bool wait) {
        this->station_time_hole = 0;
        this->charge_number = charge_number;
        this->load_assigned = 0;
        this->flow_in_number.clear();
        this->no_charge_list.clear();
        this->no_charge_number = 0;
        this->empty_list.clear();
        this->empty_number = 0;
        this->min_power = 0;
        this->max_power = 0;
        this->charge_power = 0;
        this->car_number = 0;
        this->make_init_list();
        this->show = false;
        this->wait = wait;
        this->line = 0;
        this->constant_charging = false;
        std::cout << "StationBase initialized!" << std::endl;
    };

    ////////////////////////////
    void catch_load_wrapper1() {
        return catch_load();
    };

    void catch_load_wrapper2(float load) {
        return catch_load(load);
    };
    ////////////////////////////

    void catch_load() {
        this->load_assigned = this->max_power;
    };

    void catch_load(float load) {
        if (load > this->max_power) {
            load = this->max_power;
        } else if (load < this->min_power) {
            load = this->min_power;
        } else {
        }
        this->load_assigned = load;
    };

    virtual void calculate_output() {
        float now_power = 0;
        int number = 0;
        for (int i = 0; i < this->charge_number; i++) {
            if (this->situation["car"][i] > 0.5) {
                number += 1;
                if (this->situation["charge"][i] > 0.5) {
                    now_power += this->situation["power"][i];
                }
            }
        }
        this->charge_power = now_power;
        this->car_number = number;
        std::cout << "virtual calculate_output" << std::endl;
    };

    void print_situation() override {
        PrintUtil::Print_Two_Dimension_Map<std::string, int, float>(this->situation);
        int first_size;
        int second_sizes = 0;
        std::vector<int> second_size;
        first_size = this->situation.size();
        for (auto &it_one: this->situation) {
            int size_temp = it_one.second.size();
            second_sizes += size_temp;
            second_size.push_back(size_temp);
        }
        std::cout << "situation fist size " << first_size << std::endl;
        std::cout << "situation second size " << second_sizes << std::endl;
        PrintUtil::Print_Vector(second_size);
        std::cout << "Station situation is already printed!" << std::endl;
    };

    void tell_empty() {
        this->find_empty();
        if (this->show) {
            std::cout << "empty number " << this->empty_number << std::endl;
            PrintUtil::Print_Vector(this->empty_list);
        }
    };

    void tell_chargeable() {
        this->find_chargeable();
        if (this->show) {
            std::cout << "chargeable number " << this->no_charge_number << std::endl;
            PrintUtil::Print_Vector(this->no_charge_list);
        }
    };

    void assign_car() {
        int assign_number;
        if (this->wait) {
            assign_number = std::min<int>((this->line + this->flow_in_number.back()), this->empty_number);
            this->line = this->line + this->flow_in_number.back() - assign_number;
            this->line = std::min<int>(this->line, this->max_line);
        } else {
            assign_number = std::min<int>(this->flow_in_number.back(), this->empty_number);
        }

        for (int i = 0; i < assign_number; i++) {
            this->situation["assign"][this->empty_list[i]] = 1;
        }
    };

    virtual void receive_car() {
        std::cout << "virtual receive_car" << std::endl;
    };

    virtual void assign_on_off() {
        std::cout << "virtual assign_on_off" << std::endl;
    };


protected:
    void find_empty() {
        this->empty_list.clear();
        this->empty_number = 0;
        for (int i = 0; i < this->charge_number; i++) {
            if (this->situation["car"][i] <= 0.5) {
                this->empty_list.push_back(i);
                this->empty_number += 1;
            }
        }
    };

    void find_chargeable() {
        this->no_charge_list.clear();
        this->no_charge_number = 0;
        for (int i = 0; i < this->charge_number; i++) {
            if (this->situation["charge"][i] <= 0.5) {
                this->no_charge_list.push_back(i);
                this->no_charge_number += 1;
            }
        }
    };

};

// tested
class UtilSlow {
public:
    ////////////////////////////
    static float slow_time_to_power_wrapper1(float charge_time) {
        return slow_time_to_power(charge_time);
    };

    static float slow_time_to_power_wrapper2(float charge_time, bool constant_power) {
        return slow_time_to_power(charge_time, constant_power);
    };

    static float slow_time_to_soc_wrapper1(float charge_time) {
        return slow_time_to_soc(charge_time);
    };

    static float slow_time_to_soc_wrapper2(float charge_time, bool constant_power) {
        return slow_time_to_soc(charge_time, constant_power);
    };

    static float slow_soc_to_time_wrapper1(float soc) {
        return slow_soc_to_time(soc);
    };

    static float slow_soc_to_time_wrapper2(float soc, bool constant_power) {
        return slow_soc_to_time(soc, constant_power);
    };

    ////////////////////////////
    static float slow_time_to_power(float charge_time, bool constant_power = false) {
        if (constant_power) {
            if (14.68 >= charge_time and charge_time >= 0) {
                return 5.254973139368931;
            } else {
                return 0;
            }
        } else {
            if (charge_time < 2.33 * 4) {
                return b_part1(charge_time / 4);
            } else if (charge_time < 3.67 * 4) {
                return b_part2(charge_time / 4);
            } else {
                return 0;
            }
        }
    };

    static float slow_time_to_soc(float charge_time, bool constant_power = false) {
        if (constant_power) {
            if (charge_time <= 0) {
                return 0;
            } else if (charge_time >= 14.68) {
                return 100;
            } else {
                return 100 * charge_time / 14.68;
            }
        } else {
            return 100 * c_hole(charge_time) / 19.285746346634653;
        }
    };

    static float slow_soc_to_time(float soc, bool constant_power = false) {
        if (constant_power) {
            if (soc <= 0) {
                return 0;
            } else if (soc >= 100) {
                return 14.68;
            } else {
                return 14.68 * soc / 100;
            }

        } else {
            if (soc < 0) {
                return 0;
            } else if (0 <= soc and soc <= 73.89239629561729) {
                return s_t_t_1(soc);
            } else if (73.89239629561729 < soc and soc <= 100) {
                return s_t_t_2(soc) + 0.2012016075138625 * (soc - 73.89239629561729) / 26.10760370438271;
            } else {
                return 14.68;
            }
        }
    };

private:
    static float b_part1(float x) {
        return -0.002056 * pow(x, 4) + 0.00921 * pow(x, 3) + 0.03562 * pow(x, 2) + 0.02379 * x + 6.007;
    };

    static float b_part2(float x) {
        return (-4.041 * x + 21.1) / (x - 0.485);
    };

    static float c_part1(float x) {
        return -0.0004112 * pow(x, 5) + 0.0023025 * pow(x, 4) + (0.03562 / 3) * pow(x, 3) + 0.011895 * pow(x, 2) +
               6.007 * x;
    };

    static float c_part2(float x) {
        return -4.041 * x + 19.140115 * log(std::abs(x - 0.485)) + 11.943306312699628;
    };

    static float c_hole(float x) {
        if (x <= 0) {
            return 0;
        } else if (x <= 2.33 * 4) {
            return c_part1(x / 4);
        } else if (x <= 3.67 * 4) {
            return c_part2(x / 4);
        } else {
            return c_part2(3.67);
        }
    };

    static float s_t_t_1(float soc) {
        return (-4.276 * pow(10, -5)) * pow(soc, 2) + 0.1295 * soc;
    };

    static float s_t_t_2(float soc) {
        return (4.742 * pow(10, -6)) * pow(soc, 4) - 0.001529 * pow(soc, 3) + 0.1871 * pow(soc, 2) - 10.15 * soc +
               213.1 +
               0.1787983924863248;
    };

};

// tested
class UtilFast {
public:
    ////////////////////////////
    static float fast_time_to_power_wrapper1(float charge_time) {
        return fast_time_to_power(charge_time);
    };

    static float fast_time_to_power_wrapper2(float charge_time, bool constant_power) {
        return fast_time_to_power(charge_time, constant_power);
    };

    static float fast_time_to_soc_wrapper1(float charge_time) {
        return fast_time_to_soc(charge_time);
    };

    static float fast_time_to_soc_wrapper2(float charge_time, bool constant_power) {
        return fast_time_to_soc(charge_time, constant_power);
    };

    static float fast_soc_to_time_wrapper1(float soc) {
        return fast_soc_to_time(soc);
    };

    static float fast_soc_to_time_wrapper2(float soc, bool constant_power) {
        return fast_soc_to_time(soc, constant_power);
    };

    ////////////////////////////
    static float fast_time_to_power(float charge_time, bool constant_power = false) {
        if (constant_power) {
            if (3.4133333333333336 >= charge_time and charge_time >= 0) {
                return 36.44764034125146;
            } else {
                return 0;
            }
        } else {
            if (charge_time >= 0 and charge_time < (28.7 / 15)) {
                return a_part1(charge_time * 15);
            } else if (charge_time >= 0 and charge_time < (51.2 / 15)) {
                return a_part2(charge_time * 15);
            } else {
                return 0;
            }
        }
    };

    static float fast_time_to_soc(float charge_time, bool constant_power = false) {
        if (constant_power) {
            if (charge_time <= 0) {
                return 0;
            } else if (charge_time >= 3.4133333333333336) {
                return 100;
            } else {
                return 100 * charge_time / 3.4133333333333336;
            }
        } else {
            if (charge_time <= 0) {
                return 0;
            } else if (charge_time <= 28.7 / 15) {
                return aa_part1(charge_time * 15) * (100 / aa_part2(51.2));
            } else if (charge_time <= 51.2 / 15) {
                return aa_part2(charge_time * 15) * (100 / aa_part2(51.2));
            } else {
                return 100;
            }
        }
    };

    static float fast_soc_to_time(float soc, bool constant_power = false) {
        if (constant_power) {
            if (soc <= 0) {
                return 0;
            } else if (soc >= 100) {
                return 3.4133333333333336;
            } else {
                return 3.4133333333333336 * soc / 100;
            }

        } else {
            if (soc <= 0) {
                return 0;
            } else if (soc >= 100) {
                return 51.2 / 15;
            } else {
                return matlab_fitted_curve(norm_soc(soc));
            }

        }
    };

private:
    static float a_part1(float x) {
        return 0.7194 * exp(0.053 * x) + 47.78;
    };

    static float a_part2(float x) {
        return 0.0002253 * pow(x, 4) - 0.03572 * pow(x, 3) + 2.016 * pow(x, 2) - 48.76 * x + 457.7;
    };

    static float aa_part1(float x) {
        float aa_part1_c = (0.7194 / 0.053) * exp(0);
        return (0.7194 / 0.053) * exp(0.053 * x) + 50.15 * x - aa_part1_c;
    };

    static float aa_part2(float x) {
        float aa_part2_c = aa_part1(28.7) -
                           ((0.0002253 / 5) * pow(28.7, 5) - (0.03572 / 4) * pow(28.7, 4) + (2.016 / 3) * pow(28.7, 3) -
                            (48.76 / 2) * pow(28.7, 2) + 457.7 * 28.7);
        return (0.0002253 / 5) * pow(x, 5) - (0.03572 / 4) * pow(x, 4) + (2.016 / 3) * pow(x, 3) -
               (48.76 / 2) * pow(x, 2) +
               457.7 * x + aa_part2_c;
    };

    static float matlab_fitted_curve(float x) {
        float p1 = -18.18;
        float p2 = 9.559;
        float p3 = 48.99;
        float p4 = -62.97;
        float p5 = 29.09;
        float q1 = -23.9;
        float q2 = 56.48;
        float q3 = -50.12;
        float q4 = 18.96;
        float temp = (p1 * pow(x, 4) + p2 * pow(x, 3) + p3 * pow(x, 2) + p4 * x + p5) /
                     (pow(x, 4) + q1 * pow(x, 3) + q2 * pow(x, 2) + q3 * x + q4);
        return temp;
    };

    static float norm_soc(float x) {
        float mean = 61.43;
        float std = 31.48;
        return (x - mean) / std;
    };
};

// tested
class PoissonNumber {
public:
    static int give_car_number_wrt_poisson(int what_time) {
        int car_max = 300;
        std::vector<double> compare_list = car_flow_possibility_list[what_time];
        float compare_possible = RandomUtil::uniform_rand(0, 1);
        int item_id = 0;
        for (double &item: compare_list) {
            if (item >= compare_possible) {
                return item_id;
            }
            item_id++;
        }
        return car_max;
    };

    static int ev_car_number_wrt_poisson(int what_time) {
        float possible_in = 0.1;
        float permeability = 0.2;
        float po_ev_number = possible_in * permeability * give_car_number_wrt_poisson(what_time);
        return std::round(po_ev_number);
    };

    static int hv_car_number_wrt_poisson(int what_time) {
        float hv_possible_in = 0.3;
        float hv_permeability = 0.01;
        return std::round(hv_possible_in * hv_permeability * PoissonNumber::give_car_number_wrt_poisson(what_time));
    };
};

// tested
class CarArriveRandom {
public:
    ////////////////////////////
    static int init_station_car_number_wrapper1() {
        return init_station_car_number();
    };

    static int init_station_car_number_wrapper2(int mu) {
        return init_station_car_number(mu, 3);
    };

    static int init_station_car_number_wrapper3(int theta) {
        return init_station_car_number(25, theta);
    };

    static int init_station_car_number_wrapper4(int mu, int theta) {
        return init_station_car_number(mu, theta);
    };

    ////////////////////////////
    static float mk_soc() {
        std::normal_distribution<double> normal_distribution(7.0, 3.0);
        float driver_experience = normal_distribution(e);
        if (driver_experience < 1.0) {
            driver_experience = 1.0;
        } else if (driver_experience > 10.0) {
            driver_experience = 10.0;
        }
        float soc = 75.0 - 5.0 * driver_experience;
        return soc;
    };

    static int mk_late_time(const std::string &charge_type) {
        float car_number;
        if (charge_type == "slow" or charge_type == "Slow" or charge_type == "SLOW") {
            std::normal_distribution<float> normal_distribution(2.0, 2.0);
            car_number = normal_distribution(e);
        } else if (charge_type == "fast" or charge_type == "Fast" or charge_type == "FAST") {
            std::normal_distribution<float> normal_distribution(1.0, 1.0);
            car_number = normal_distribution(e);
        } else {
            std::cout << "position class must be 'fast' or 'slow' " << std::endl;
            car_number = 0.0;
        }
        int duration = std::max(0, (int) std::round(car_number));
        return duration;
    };

    static int init_station_car_number(int mu = 25, int theta = 3) {
        std::normal_distribution<float> normal_distribution(mu, 1.0);
        float car_number = normal_distribution(e);
        int temp = std::round(car_number);
        if (temp > mu + theta) {
            temp = mu + theta;
        } else if (temp < mu - theta) {
            temp = mu - theta;
        }
        return temp;
    };
};

// tested
class SlowPile : public ChargePositionBase {
public:
    SlowPile() {
        std::cout << "no use" << std::endl;
    };

    SlowPile(int position_input, Station *station_name_input) : ChargePositionBase(position_input, station_name_input) {
    };

    bool operator==(SlowPile const &t) const {
        return t.position == this->position && t.station_name == this->station_name;
    }

    bool operator!=(SlowPile const &t) const {
        return t.position != this->position || t.station_name != this->station_name;
    }


    void add_car() override {
        this->arrive_soc = CarArriveRandom::mk_soc();
        this->current_soc = this->arrive_soc;
        this->target_soc = RandomUtil::uniform_rand(80, 100);
        int must_needed = calculate_min_charging_time();
        this->stay_time = must_needed + CarArriveRandom::mk_late_time("slow");
        this->already_stay_time = 0;
        this->occupy_position();
        this->station_name->situation["power"][this->position] = UtilSlow::slow_time_to_power(
                UtilSlow::slow_soc_to_time(this->current_soc, this->station_name->constant_charging),
                this->station_name->constant_charging);
        this->station_name->situation["init_soc"][this->position] = this->arrive_soc;
        this->station_name->situation["target_soc"][this->position] = this->target_soc;
    };

    void calculate_needed() override {
        float needed_time = UtilSlow::slow_soc_to_time(this->target_soc, this->station_name->constant_charging) -
                            UtilSlow::slow_soc_to_time(this->current_soc, this->station_name->constant_charging);
        int time_left = this->stay_time - this->already_stay_time;

        if (needed_time > 0) {
            if (time_left <= std::ceil(needed_time)) {
                this->must_charge = true;
                this->emergency = 10;
                this->station_name->situation["emergency"][this->position] = 10;
            } else {
                this->must_charge = false;
                this->emergency = pow((needed_time / (float) time_left), 2);
                this->station_name->situation["emergency"][this->position] = pow((needed_time / (float) time_left), 2);
            }
        } else {
            this->station_name->situation["emergency"][this->position] = 0.0;
        }
        this->station_name->situation["soc"][this->position] = this->current_soc;
    };

    void car_step() override {
        float temp_time = UtilSlow::slow_soc_to_time(this->current_soc, this->station_name->constant_charging) + 1;
        this->current_soc = UtilSlow::slow_time_to_soc(temp_time, this->station_name->constant_charging);
        this->current_power = UtilSlow::slow_time_to_power(temp_time, this->station_name->constant_charging);
        this->station_name->situation["power"][this->position] = UtilSlow::slow_time_to_power(temp_time,
                                                                                              this->station_name->constant_charging);
        for (int i = 0; i < this->station_name->charge_number; i++) {
            this->station_name->situation["assign"][i] = 0;
        }
    };


    void remove_car(bool quick_leave) override {
        this->already_stay_time += 1;
        int time_left = this->stay_time - this->already_stay_time;
        if (time_left <= 0) {
            if (std::ceil(this->current_soc) < std::floor(this->target_soc)) {
                std::cout << "slow charge is not complete " << std::endl;
                std::cout << "slow charge time " << time_left << std::endl;
                std::cout << "slow current " << this->current_soc << std::endl;
                std::cout << "slow target " << this->target_soc << std::endl;
            }
            this->reset_position();
        }
        if (quick_leave) {
            if (this->current_soc >= this->target_soc) {
//                std::cout << "charging complete before the leaving time!" << std::endl;
                this->reset_position();
            }
        }
    };

private:
    int calculate_min_charging_time() {
        float needed_time = UtilSlow::slow_soc_to_time(this->target_soc, this->station_name->constant_charging) -
                            UtilSlow::slow_soc_to_time(this->current_soc, this->station_name->constant_charging);
        return std::ceil(needed_time);
    };
};

// tested
class FastPile : public ChargePositionBase {
public:
    FastPile(int position_input, Station *station_name_input) : ChargePositionBase(position_input,
                                                                                   station_name_input) {
    };

    void add_car() override {
        this->arrive_soc = CarArriveRandom::mk_soc();
        this->current_soc = this->arrive_soc;
        this->target_soc = RandomUtil::uniform_rand(80, 100);
        int must_needed = calculate_min_charging_time();
        this->stay_time = must_needed + CarArriveRandom::mk_late_time("slow");
        this->already_stay_time = 0;
        this->occupy_position();
        this->station_name->situation["power"][this->position] = UtilFast::fast_time_to_power(
                UtilFast::fast_soc_to_time(this->current_soc, this->station_name->constant_charging),
                this->station_name->constant_charging);
    };

    void calculate_needed() override {
        float needed_time = UtilFast::fast_soc_to_time(this->target_soc, this->station_name->constant_charging) -
                            UtilFast::fast_soc_to_time(this->current_soc, this->station_name->constant_charging);
        int time_left = this->stay_time - this->already_stay_time;

        if (needed_time > 0) {
            if (time_left <= std::ceil(needed_time)) {
                this->must_charge = true;
                this->emergency = 10;
                this->station_name->situation["emergency"][this->position] = 10;
            } else {
                this->must_charge = false;
                this->emergency = pow((needed_time / (float) time_left), 2);
                this->station_name->situation["emergency"][this->position] = pow((needed_time / (float) time_left), 2);
            }
        } else {
            this->station_name->situation["emergency"][this->position] = 0.0;
        }
    };

    void car_step() override {
        float temp_time = UtilFast::fast_soc_to_time(this->current_soc, this->station_name->constant_charging) + 1;
        this->current_soc = UtilFast::fast_time_to_soc(temp_time, this->station_name->constant_charging);
        this->current_power = UtilFast::fast_time_to_power(temp_time, this->station_name->constant_charging);
        this->station_name->situation["power"][this->position] = UtilFast::fast_time_to_power(temp_time,
                                                                                              this->station_name->constant_charging);
        for (int i = 0; i < this->station_name->charge_number; i++) {
            this->station_name->situation["assign"][i] = 0;
        }
    };


    void remove_car(bool quick_leave) override {
        this->already_stay_time += 1;
        int time_left = this->stay_time - this->already_stay_time;
        if (time_left <= 0) {
            if (std::ceil(this->current_soc) < std::floor(this->target_soc)) {
                std::cout << "fast charge is not complete " << std::endl;
                std::cout << "fast charge time " << time_left << std::endl;
                std::cout << "fast current " << this->current_soc << std::endl;
                std::cout << "fast target " << this->target_soc << std::endl;
            }
            this->reset_position();
        }
        if (quick_leave) {
            if (this->current_soc >= this->target_soc) {
//                std::cout << "charging complete before the leaving time!" << std::endl;
                this->reset_position();
            }
        }
    };

private:
    int calculate_min_charging_time() {
        float needed_time = UtilFast::fast_soc_to_time(this->target_soc, this->station_name->constant_charging) -
                            UtilFast::fast_soc_to_time(this->current_soc, this->station_name->constant_charging);
        return std::ceil(needed_time);
    };
};

class SlowChargeStation : public StationBase {
public:
    ////////////////////////////
    void evs_step_wrapper1(float action) {
        return evs_step(action);
    };

    void evs_step_wrapper2(float action, bool test) {
        return evs_step(action, test);
    };

    void evs_step_wrapper3(std::vector<float> actions) {
        return evs_step(std::move(actions), false);
    };
    ////////////////////////////
    bool quick_leave = true;
    float charge_power_upper_limit;
    float constant_power;
    float transformer_limit;
    std::map<std::string, SlowPile> positions;
    std::vector<float> charging_actions; //add 1

    explicit SlowChargeStation(int charge_number) : StationBase(charge_number, "slow", true) {
        this->set_position("slow");
        this->constant_charging = false;
        this->charge_power_upper_limit = 7;
        this->evs_reset();
        this->constant_power = 5.254973139368931;
        this->transformer_limit = this->constant_power * this->charge_number;
        std::cout << "SlowChargeStation initialized!" << std::endl;
    };

    SlowChargeStation(int charge_number, bool constant_charging) : StationBase(charge_number, "slow", true) {
        this->set_position("slow");
        this->constant_charging = constant_charging;
        this->charge_power_upper_limit = 7;
        this->evs_reset();
        this->constant_power = 5.254973139368931;
        this->transformer_limit = this->constant_power * this->charge_number;
        std::cout << "SlowChargeStation initialized!" << std::endl;
    };

    SlowChargeStation(int charge_number, bool wait, bool constant_charging) : StationBase(charge_number, "slow", wait) {
        this->set_position("slow");
        this->constant_charging = constant_charging;
        this->charge_power_upper_limit = 7;
        this->evs_reset();
        this->constant_power = 5.254973139368931;
        this->transformer_limit = this->constant_power * this->charge_number;
        std::cout << "SlowChargeStation initialized!" << std::endl;
    };

    SlowChargeStation(int charge_number, bool wait, bool constant_charging, const std::string &position_class)
            : StationBase(charge_number, position_class, wait) {
        this->set_position(position_class);
        this->constant_charging = constant_charging;
        this->charge_power_upper_limit = 7;
        this->evs_reset();
        this->constant_power = 5.254973139368931;
        this->transformer_limit = this->constant_power * this->charge_number;
        std::cout << "SlowChargeStation initialized!" << std::endl;
    };

    void evs_step(float action, bool test = false) {
        this->calculate_output();
        this->catch_load(action);
        this->assign_on_off();
        if (!test) {
            for (int change_car = 0; change_car < this->charge_number; change_car++) {
                if (this->situation["charge"][change_car]) {
                    this->positions.at("SP" + std::to_string(change_car)).car_step();
                }
                if (this->situation["car"][change_car]) {
                    this->positions.at("SP" + std::to_string(change_car)).remove_car(this->quick_leave);
                }
            }
            this->receive_car(false);
            this->station_time_hole = (this->station_time_hole + 1) % 96;
        }
        this->calculate_output();
    };

    void evs_step(std::vector<float> actions, bool test = false) {
        this->calculate_output();

        actions = this->judge_feasibility(actions);

        this->assign_on_off_piece(actions);
        if (!test) {
            for (int change_car = 0; change_car < this->charge_number; change_car++) {
                if (this->situation["charge"][change_car]) {
                    this->positions.at("SP" + std::to_string(change_car)).car_step();
                }
                if (this->situation["car"][change_car]) {
                    this->positions.at("SP" + std::to_string(change_car)).remove_car(this->quick_leave);
                }
            }
            this->receive_car(false);
            this->station_time_hole = (this->station_time_hole + 1) % 96;
        }
        this->calculate_output();
    };

    void evs_reset() {
        this->flow_in_number.clear();
        this->line = 0;
        this->station_time_hole = 0;
        this->load_assigned = 0;
        this->no_charge_list.clear();
        this->no_charge_number = 0;
        this->empty_list.clear();
        this->empty_number = 0;
        this->min_power = 0;
        this->max_power = 0;
        this->charge_power = 0;
        this->car_number = 0;
        this->situation.clear();
        this->make_init_list();
        this->charging_actions.clear(); //add 2

        for (int i = 0; i < this->charge_number; i++) {
            this->positions.at("SP" + std::to_string(i)).pl_reset();
        }
        this->receive_car(true);
        this->calculate_output();
    };

    void calculate_output() override {
        for (int needed_where = 0; needed_where < this->charge_number; needed_where++) {
            if (this->situation["car"][needed_where] > 0.5) {
                this->positions.at("SP" + std::to_string(needed_where)).calculate_needed();
            }
        }
        float min_power = 0;
        float max_power = 0;
        float now_power = 0;
        int number = 0;

        for (int out_count = 0; out_count < this->charge_number; out_count++) {
            if (this->situation["car"][out_count] > 0.5) {
                number += 1;
                max_power += this->situation["power"][out_count];
                if (this->situation["emergency"][out_count] > 8) {
                    min_power += this->situation["power"][out_count];
                }
                if (this->situation["charge"][out_count] <= 1.1 and this->situation["charge"][out_count] >= 0.9) {
                    now_power += this->situation["power"][out_count];
                }
            }
        }

        this->min_power = min_power;
        this->max_power = max_power;
        this->charge_power = now_power;
        this->car_number = number;
    };

private:
    void set_position(const std::string &position_class) {
        this->positions.clear();
        for (int i = 0; i < this->charge_number; i++) {
            this->positions.insert(make_pair("SP" + std::to_string(i), SlowPile(i, this)));
        }
        std::cout << "slow position generated!" << std::endl;
    };

    void receive_car(bool reset_evs = false) {
        this->tell_empty();
        int in_car;
        if (reset_evs) {
            in_car = CarArriveRandom::init_station_car_number(round(this->charge_number / 6));
        } else {
            int in_car_time = this->station_time_hole % 96;
            in_car = PoissonNumber::ev_car_number_wrt_poisson(in_car_time);
//            std::cout<<"in ev "<<in_car<<std::endl;
        }
        // TODO: leave & arrival possibility is added here!   begin
        float a;
        float true_line = 0;
        float leave_possibility;
        for (int wait_id = 0; wait_id < this->line; wait_id++) {
            leave_possibility = 0.1 * logf(wait_id + 1);
            a = RandomUtil::uniform_rand(0, 1);
            if (a > leave_possibility) {
                true_line += 1;
            }
        }
        this->line = true_line;
        /////////////////////////////////
        int true_in_car = 0;
        float arrival_stay_possibility;
        for (int arrive_id = 0; arrive_id < in_car; arrive_id++) {
            a = RandomUtil::uniform_rand(0, 1);
            arrival_stay_possibility = expf(-(0.01 * (this->line + arrive_id)));
            if (a <= arrival_stay_possibility && arrive_id <= this->charge_number) {
                true_in_car += 1;
            }
        }
        // TODO: end

        this->flow_in_number.push_back(true_in_car);
        this->assign_car();
        for (int assign_where = 0; assign_where < this->charge_number; assign_where++) {
            if (this->situation["assign"][assign_where] > 0.5) {
                this->positions.at("SP" + std::to_string(assign_where)).add_car();
            }
        }
        for (int i = 0; i < this->charge_number; i++) {
            this->situation["assign"][i] = 0;
        }
    };

    void assign_on_off() override {
        if (this->constant_charging) {
            for (int i = 0; i < this->charge_number; i++) {
                this->situation["charge"][i] = 0;
            }
            ///////////////////////////////  sort start
            std::map<int, float> emergency_temp = this->situation["emergency"];
            std::multimap<float, int> swap_emergency_temp;

            for (auto &it_one: emergency_temp) {
                swap_emergency_temp.insert(std::make_pair(-it_one.second, it_one.first));
            }

            std::vector<int> sort_number;
            sort_number.clear();

            for (auto &it: swap_emergency_temp) {
                sort_number.push_back(it.second);
            }
            ///////////////////////////////  sort end
            int constant_charge_number = std::round(this->load_assigned / this->constant_power);

            int assigned = 0;

            for (int have_car = 0; have_car < this->charge_number; have_car++) {
                if (this->situation["car"][sort_number[have_car]] == 1 and assigned < constant_charge_number) {
                    this->situation["charge"][sort_number[have_car]] = 1;
                    assigned += 1;
                }

            }
        } else {
            for (int i = 0; i < this->charge_number; i++) {
                this->situation["charge"][i] = 0;
            }
            std::vector<float> added_power;
            std::vector<int> added_power_index;
            tie(added_power, added_power_index) = this->rank_power_add();
            for (int assign_car = 0; assign_car < added_power.size(); assign_car++) {
                if (this->load_assigned + 0.0001 >= added_power[assign_car]) {
                    this->situation["charge"][added_power_index[assign_car]] = 1;
                }
            }
        }
    };

    void assign_on_off_piece(std::vector<float> actions) {
        for (int i = 0; i < this->charge_number; i++) {
            this->situation["charge"][i] = 0;
        }
        for (int have_car = 0; have_car < this->charge_number; have_car++) {
            if (this->situation["car"][have_car] == 1 and actions[have_car] == 1) {
                this->situation["charge"][have_car] = 1;
            }
        }
    };

    std::tuple<std::vector<float>, std::vector<int>> rank_power_add() {
        ///////////////////////////////  sort start
        std::map<int, float> emergency_temp = this->situation["emergency"];
        std::multimap<float, int> swap_emergency_temp;

        for (auto &it_one: emergency_temp) {
            swap_emergency_temp.insert(std::make_pair(-it_one.second, it_one.first));
        }

        std::vector<int> sort_number;
        sort_number.clear();

        for (auto &it: swap_emergency_temp) {
            sort_number.push_back(it.second);
        }
        ///////////////////////////////  sort end
        std::vector<float> added_rank;
        float added_temp = 0;
        std::vector<int> added_number;
        for (int rank_count = 0; rank_count < this->charge_number; rank_count++) {
            if (this->situation["car"][sort_number[rank_count]] == 1) {
                added_temp += this->situation["power"][sort_number[rank_count]];
                added_rank.push_back(added_temp);
                added_number.push_back(sort_number[rank_count]);
            }
        }
        return {added_rank, added_number};
    };

    std::vector<float> judge_feasibility(std::vector<float> actions) {
        for (int i = 0; i < this->charge_number; i++) {
            if (this->situation["emergency"][i] >= 1.01 and this->situation["car"][i] == 1) {
                actions[i] = 1;
            } else if (this->situation["car"][i] < 1) {
                actions[i] = 0;
            }
        }
        return actions;
    };
};

class FastChargeStation : public StationBase {
public:
    ////////////////////////////
    void evs_step_wrapper1(float action) {
        return evs_step(action);
    };

    void evs_step_wrapper2(float action, bool test) {
        return evs_step(action, test);
    };

    void evs_step_wrapper3(std::vector<float> actions) {
        return evs_step(std::move(actions), false);
    };
    ////////////////////////////
    bool quick_leave = true;
    float charge_power_upper_limit;
    float constant_power;
    float transformer_limit;
    std::map<std::string, FastPile> positions;
    std::vector<float> charging_actions; //add 1

    explicit FastChargeStation(int charge_number) : StationBase(charge_number, "fast", true) {
        this->set_position("fast");
        this->constant_charging = false;
        this->charge_power_upper_limit = 60;
        this->evs_reset();
        this->constant_power = 36.44764034125146;
        this->transformer_limit = this->constant_power * this->charge_number;
        std::cout << "FastChargeStation initialized!" << std::endl;
    };

    FastChargeStation(int charge_number, bool constant_charging) : StationBase(charge_number, "fast", true) {
        this->set_position("fast");
        this->constant_charging = constant_charging;
        this->charge_power_upper_limit = 60;
        this->evs_reset();
        this->constant_power = 36.44764034125146;
        this->transformer_limit = this->constant_power * this->charge_number;
        std::cout << "FastChargeStation initialized!" << std::endl;
    };

    FastChargeStation(int charge_number, bool wait, bool constant_charging) : StationBase(charge_number, "fast", wait) {
        this->set_position("fast");
        this->constant_charging = constant_charging;
        this->charge_power_upper_limit = 60;
        this->evs_reset();
        this->constant_power = 36.44764034125146;
        this->transformer_limit = this->constant_power * this->charge_number;
        std::cout << "FastChargeStation initialized!" << std::endl;
    };

    FastChargeStation(int charge_number, bool wait, bool constant_charging, const std::string &position_class)
            : StationBase(charge_number, position_class, wait) {
        this->set_position(position_class);
        this->constant_charging = constant_charging;
        this->charge_power_upper_limit = 60;
        this->evs_reset();
        this->constant_power = 36.44764034125146;
        this->transformer_limit = this->constant_power * this->charge_number;
        std::cout << "FastChargeStation initialized!" << std::endl;
    };


    void evs_step(float action, bool test = false) {
        this->calculate_output();
        this->catch_load(action);
        this->assign_on_off();
        if (!test) {
            for (int change_car = 0; change_car < this->charge_number; change_car++) {
                if (this->situation["charge"][change_car]) {
                    this->positions.at("FP" + std::to_string(change_car)).car_step();
                }
                if (this->situation["car"][change_car]) {
                    this->positions.at("FP" + std::to_string(change_car)).remove_car(this->quick_leave);
                }
            }
            this->receive_car();
            this->station_time_hole = (this->station_time_hole + 1) % 96;
        }
        this->calculate_output();
    };

    void evs_step(std::vector<float> actions, bool test = false) {
        this->calculate_output();

        actions = this->judge_feasibility(actions);

        this->assign_on_off_piece(actions);
        if (!test) {
            for (int change_car = 0; change_car < this->charge_number; change_car++) {
                if (this->situation["charge"][change_car]) {
                    this->positions.at("FP" + std::to_string(change_car)).car_step();
                }
                if (this->situation["car"][change_car]) {
                    this->positions.at("FP" + std::to_string(change_car)).remove_car(this->quick_leave);
                }
            }
            this->receive_car(false);
            this->station_time_hole = (this->station_time_hole + 1) % 96;
        }
        this->calculate_output();
    };

    void evs_reset() {
        this->flow_in_number.clear();
        this->line = 0;
        this->station_time_hole = 0;
        this->load_assigned = 0;
        this->no_charge_list.clear();
        this->no_charge_number = 0;
        this->empty_list.clear();
        this->empty_number = 0;
        this->min_power = 0;
        this->max_power = 0;
        this->charge_power = 0;
        this->car_number = 0;
        this->situation.clear();
        this->make_init_list();
        this->charging_actions.clear(); //add 2

        for (int i = 0; i < this->charge_number; i++) {
            this->positions.at("FP" + std::to_string(i)).pl_reset();
        }
        this->receive_car(true);
        this->calculate_output();
    };

    void calculate_output() override {
        for (int needed_where = 0; needed_where < this->charge_number; needed_where++) {
            if (this->situation["car"][needed_where] > 0.5) {
                this->positions.at("FP" + std::to_string(needed_where)).calculate_needed();
            }
        }
        float min_power = 0;
        float max_power = 0;
        float now_power = 0;
        int number = 0;

        for (int out_count = 0; out_count < this->charge_number; out_count++) {
            if (this->situation["car"][out_count] > 0.5) {
                number += 1;
                max_power += this->situation["power"][out_count];
                if (this->situation["emergency"][out_count] > 8) {
                    min_power += this->situation["power"][out_count];
                }
                if (this->situation["charge"][out_count] <= 1.1 and this->situation["charge"][out_count] >= 0.9) {
                    now_power += this->situation["power"][out_count];
                }
            }
        }

        this->min_power = min_power;
        this->max_power = max_power;
        this->charge_power = now_power;
        this->car_number = number;
    };

private:
    void set_position(const std::string &position_class) {
        this->positions.clear();
        for (int i = 0; i < this->charge_number; i++) {
            this->positions.insert(make_pair("FP" + std::to_string(i), FastPile(i, this)));
        }
        std::cout << "fast position generated!" << std::endl;
    };

    void receive_car(bool reset_evs = false) {
        this->tell_empty();
        int in_car;
        if (reset_evs) {
            in_car = CarArriveRandom::init_station_car_number(round(this->charge_number / 6));
        } else {
            int in_car_time = this->station_time_hole % 96;
            in_car = PoissonNumber::ev_car_number_wrt_poisson(in_car_time);
        }

        // TODO: leave & arrival possibility is added here!   begin
        float a;
        float true_line = 0;
        float leave_possibility;
        for (int wait_id = 0; wait_id < this->line; wait_id++) {
            leave_possibility = 0.1 * logf(wait_id + 1);
            a = RandomUtil::uniform_rand(0, 1);
            if (a > leave_possibility) {
                true_line += 1;
            }
        }
        this->line = true_line;
        /////////////////////////////////
        int true_in_car = 0;
        float arrival_stay_possibility;
        for (int arrive_id = 0; arrive_id < in_car; arrive_id++) {
            a = RandomUtil::uniform_rand(0, 1);
            arrival_stay_possibility = expf(-(0.01 * (this->line + arrive_id)));
            if (a <= arrival_stay_possibility && arrive_id <= this->charge_number) {
                true_in_car += 1;
            }
        }
        // TODO: end

        this->flow_in_number.push_back(in_car);
        this->assign_car();
        for (int assign_where = 0; assign_where < this->charge_number; assign_where++) {
            if (this->situation["assign"][assign_where] > 0.5) {
                this->positions.at("FP" + std::to_string(assign_where)).add_car();
            }
        }
        for (int i = 0; i < this->charge_number; i++) {
            this->situation["assign"][i] = 0;
        }
    };

    void assign_on_off() override {
        if (this->constant_charging) {
            for (int i = 0; i < this->charge_number; i++) {
                this->situation["charge"][i] = 0;
            }
            ///////////////////////////////  sort start
            std::map<int, float> emergency_temp = this->situation["emergency"];
            std::multimap<float, int> swap_emergency_temp;

            for (auto &it_one: emergency_temp) {
                swap_emergency_temp.insert(std::make_pair(-it_one.second, it_one.first));
            }

            std::vector<int> sort_number;
            sort_number.clear();

            for (auto &it: swap_emergency_temp) {
                sort_number.push_back(it.second);
            }
            ///////////////////////////////  sort end
            int constant_charge_number = std::round(this->load_assigned / this->constant_power);

            int assigned = 0;

            for (int have_car = 0; have_car < this->charge_number; have_car++) {
                if (this->situation["car"][sort_number[have_car]] == 1 and assigned < constant_charge_number) {
                    this->situation["charge"][sort_number[have_car]] = 1;
                    assigned += 1;
                }
            }
        } else {
            for (int i = 0; i < this->charge_number; i++) {
                this->situation["charge"][i] = 0;
            }
            std::vector<float> added_power;
            std::vector<int> added_power_index;
            tie(added_power, added_power_index) = this->rank_power_add();
            for (int assign_car = 0; assign_car < added_power.size(); assign_car++) {
//                std::cout << "this->load_assigned " << this->load_assigned << std::endl;
//                std::cout << "added_power[assign_car] " << added_power[assign_car] << std::endl;
                if (this->load_assigned + 0.0001 >= added_power[assign_car]) {
                    this->situation["charge"][added_power_index[assign_car]] = 1;
                }
            }
        }
    };

    void assign_on_off_piece(std::vector<float> actions) {
        for (int i = 0; i < this->charge_number; i++) {
            this->situation["charge"][i] = 0;
        }
        for (int have_car = 0; have_car < this->charge_number; have_car++) {
            if (this->situation["car"][have_car] == 1 and actions[have_car] == 1) {
                this->situation["charge"][have_car] = 1;
            }
        }
    };

    std::tuple<std::vector<float>, std::vector<int>> rank_power_add() {
        ///////////////////////////////  sort start
        std::map<int, float> emergency_temp = this->situation["emergency"];
        std::multimap<float, int> swap_emergency_temp;

        for (auto &it_one: emergency_temp) {
            swap_emergency_temp.insert(std::make_pair(-it_one.second, it_one.first));
        }

        std::vector<int> sort_number;
        sort_number.clear();

        for (auto &it: swap_emergency_temp) {
            sort_number.push_back(it.second);
        }
        ///////////////////////////////  sort end
        std::vector<float> added_rank;
        float added_temp = 0;
        std::vector<int> added_number;
        for (int rank_count = 0; rank_count < this->charge_number; rank_count++) {
            if (this->situation["car"][sort_number[rank_count]] == 1) {
                added_temp += this->situation["power"][sort_number[rank_count]];
                added_rank.push_back(added_temp);
                added_number.push_back(sort_number[rank_count]);
            }
        }
        return {added_rank, added_number};
    };

    std::vector<float> judge_feasibility(std::vector<float> actions) {
        for (int i = 0; i < this->charge_number; i++) {
            if (this->situation["emergency"][i] >= 1.01 and this->situation["car"][i] == 1) {
                actions[i] = 1;
            } else if (this->situation["car"][i] < 1) {
                actions[i] = 0;
            }
        }
        return actions;
    };
};

#endif //LION_CPP20_SCP_H

#pragma clang diagnostic pop